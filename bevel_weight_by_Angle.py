import bpy
import bmesh
import math
import mathutils



class TOOL_OT_auto_bevel_weight(bpy.types.Operator):
    """Automatically apply Bevel Weight to active object based on angle threshold"""
    
    bl_idname = "object.auto_bevel_weight"
    bl_label = "Auto Bevel Weight"
    bl_label_short = "Auto Bevel Weight"
    bl_options = {'REGISTER', 'UNDO'}
    
    user_angle: bpy.props.IntProperty(
        name = "Angle Threshold",
        description = "Determine what angle threshold will be affected",
        default=0,
        min = 0,
        max = 360, 
    )
    boundary_select: bpy.props.BoolProperty(
        name = "Boundary Select",
        description = "Choose whether to select manifold edge",
        default = True
    )
    bev_weight: bpy.props.FloatProperty(
        name = "Bevel Weight",
        description = "Set Bevel Weight amount",
        default = 0,
        min = 0,
        max = 1
    )
    mode: bpy.props.EnumProperty(
        name = "Select Mode",
        items = [ 
            ('APPLY', "Apply Weight", "Apply new weights value to edge"),
            ('RESET', "Reset", "Reset all weights value")
        ]
    )
    
    
    def auto_bevel_weight(self, context, user_angle, boundary_select, bev_weight):
        """Automatically set bevel weight of selected object based on various parameters"""
        
        current_obj = context.active_object
        
        # Condition check to make sure tool works only on mesh object
        if current_obj is None:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}
        if current_obj.type != 'MESH':
            self.report({'WARNING'}, "Not a mesh object")
            return {'CANCELLED'}
        
        # Ensure model will be in edit mode, regardless of what user has prior to executing 
        if current_obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
            
        # Force the viewport into Edge selection mode (Vert, Edge, Face)
        context.tool_settings.mesh_select_mode = (False, True, False)
        
        bm = bmesh.from_edit_mesh(current_obj.data)
        
        # Check if bevel weight layers exist, if not create one
        bw_layer = bm.edges.layers.float.get("bevel_weight_edge")
        if bw_layer is None:
            bw_layer = bm.edges.layers.float.new("bevel_weight_edge")
        
        manifold_edges = []
        boundary_edges = []

        # Define edge types and group them in list
        for edge in bm.edges:
            if len(edge.link_faces) == 2:
                manifold_edges.append(edge)
            else:
                boundary_edges.append(edge)
                
        bm.normal_update()
        
        # Convert user_angle to radians
        user_angle_rad = math.radians(user_angle)
        
        # Loop through edges exactly once
        for edge in bm.edges:
            
            # Handle boundary edges instantly
            if edge.is_boundary:
                edge.select = boundary_select 
                edge[bw_layer] = bev_weight
                
            # Handle manifold edges
            elif len(edge.link_faces) == 2:
                face_a, face_b = edge.link_faces
                angle_rad = face_a.normal.angle(face_b.normal)
                
                # Compare the radians directly
                if angle_rad > user_angle_rad:
                    edge.select = True
                    edge[bw_layer] = bev_weight

        # Push changes back to active Edit Mode session without exiting
        bmesh.update_edit_mesh(current_obj.data)
        
        return {'FINISHED'}
    
    
    def reset_bevel_weight(self, context):
        """Clear out any Bevel Weight value"""
        
        current_obj = context.active_object
        
        # Condition check to make sure tool works only on mesh object
        if current_obj is None:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}
        if current_obj.type != 'MESH':
            self.report({'WARNING'}, "Not a mesh object")
            return {'CANCELLED'}
        
        # Ensure model will be in edit mode, regardless of what user has prior to executing 
        if current_obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
            
        # Force the viewport into Edge selection mode (Vert, Edge, Face)
        context.tool_settings.mesh_select_mode = (False, True, False)
        
        bm = bmesh.from_edit_mesh(current_obj.data)
        
        # Check if bevel weight layers exist, if not just terminate function
        bw_layer = bm.edges.layers.float.get("bevel_weight_edge")
        if bw_layer is None:
            self.report({'WARNING'}, "No bevel weight applied, nothing to reset")
            return {'CANCELLED'}
        
        # Loop through edges and set to 0 without checking existing value
        for edge in bm.edges:
            edge[bw_layer] = 0.0
        
        # Push changes back to active and exit Edit Mode
        bmesh.update_edit_mesh(current_obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return {'FINISHED'}
    
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mode", icon='MOD_EDGESPLIT', expand=True)
        layout.separator(type='LINE')
        
        if self.mode == 'APPLY':
            layout.prop(self, "boundary_select", icon='MOD_EDGESPLIT', toggle=True)
            row = layout.row(align=True)
            row = layout.split(factor=0.95)
            row.prop(self, "user_angle", expand=True)
            row.label(text="°")
            layout.prop(self, "bev_weight", expand=True)
            layout.separator(type='LINE')
 
 
    def execute(self, context):
        # Stop if function safety check failed
        if self.mode == 'APPLY':
            result = self.auto_bevel_weight(context, self.user_angle, self.boundary_select, self.bev_weight)
            if result == {'CANCELLED'}:
                return {'CANCELLED'}
            self.report({'INFO'}, f"Bevel Weight value of {self.bev_weight:.2f} has been applied to edges.")
            
        elif self.mode == 'RESET':
            result = self.reset_bevel_weight(context)
            if result == {'CANCELLED'}:
                return {'CANCELLED'}
            self.report({'INFO'}, "Mean Bevel Weight has been reset")
            
        return {'FINISHED'}
    
    
    # Bring up pop up dialog box when button is clicked
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)


classes = [
            TOOL_OT_auto_bevel_weight,
            ]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)
    
if __name__ == "__main__":
    register()