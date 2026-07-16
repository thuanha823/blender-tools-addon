import bpy
import bmesh 
import math
from bpy.props import FloatProperty

def auto_bevel_weight(obj, bevel_weight, angle_limit_rad):
    
    # Set up bmesh and red current mesh data into BMesh obj
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    # Get/create the Bevel Weight layer
    bevel_layer = bm.edges.layers.bevel_weight.verify()
    
    count = 0
    
    # Iterate over edges and check logic
    for edge in bm.edges:
        # Check if edges are connected to 2 faces (not boundary edge)
        if len(edge.link_faces) == 2:
            face1 = edge.link_faces[0]
            face2 = edge.link_faces[1]
            
            # Calculate angle between two face normals
            angle = face1.normal.angle(face2.normal)
            
            # Check the user-defined threshold (angle >= limit)
            if angle >= angle_limit_rad:
                edge[bevel_layer] = bevel_weight
                count += 1
            else:
                # Set weight to 0 for edges that doesn't meet the criteria
                edge[bevel_layer] = 0.0
    
    # Write BMesh data back to the mesh and clean up BMesh obj            
    bm.to_mesh(obj.data)
    bm.free()
    
    # Update mesh display
    obj.data.update()
    
    return count
    
    """
    bpy.context.active_object
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.transform.edge_bevelweight(value=bevel_weight)
    """
    

class VIEW3D_OT_auto_bevel(bpy.types.Operator):
    bl_idname = "tool.auto_bevel"
    bl_label = "Auto Bevel"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    bevel_value: FloatProperty(
        name="Bevel Weight Value",
        description="The value (0.0 to 1.0) to set as the Bevel Weight.",
        default=1.0,
        min=0.0,
        max=1.0,
    )
    
    angle_limit: FloatProperty(
        name="Angle Threshold",
        description="Only edges connecting faces with an angle equal to or greater than this limit will be affected.",
        default=90.0,
        min=0.0,
        max=180.0,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    def execute(self, context):
        obj = context.active_object
        
        # Make sure an obj is selected, and that it is a mesh
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh.")
            return{'CANCELLED'}
        
        # Ensure obj is in Object Mode before BMesh load
        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Convert angle limit to radians for internal math calculation    
        angle_limit_rad = math.radians(self.angle_limit)
        
        count = auto_bevel_weight(obj, self.bevel_value, angle_limit_rad)
        
        self.report({'INFO'}, f"Set Bevel Weight for {count} edges (Angle >= {self.angle_limit}°)")

        
        """
        weight = self.bevel_value
        angle = self.angle_limit
        auto_bevel_weight(bevel_weight=weight, angle_limit_rad=angle)
        """
        return{'FINISHED'}
    
    
    
class VIEW3D_PT_auto_bevel(bpy.types.Panel):
    bl_idname = "TOOL_PT_auto_bevel"
    bl_label = "Auto Bevel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Thuan\'s Addon'
    bl_parent_id = 'paneltype_realtruck_tools'
    
    def draw(self, context):
        layout = self.layout
        # layout.label(text="Auto Bevel")
        
        row = layout.row()
        row.operator("tool.auto_bevel", text="Bevel")

  
  
classes = [
            VIEW3D_OT_auto_bevel, 
            VIEW3D_PT_auto_bevel
            ]        

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()