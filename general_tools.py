import bpy
import bmesh
import math
import mathutils
import os
from mathutils import Vector
from bpy.props import BoolProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper


class TOOL_OT_quick_collection(bpy.types.Operator):
    bl_idname = "object.quick_collection"
    bl_label = "Quick Collection"
    bl_options = {'UNDO'}
    bl_description = "Create a new collection and name after active object"
    
    @classmethod
    def poll(cls, context):
        """The button will only be clickable IF there is an active object"""
        return context.active_object is not None
    
    def quick_collection(self, context):
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}
        
        collection_name = obj.name
        new_col = bpy.data.collections.new(collection_name)
        context.scene.collection.children.link(new_col)
        
        for col in obj.users_collection:
            col.objects.unlink(obj)
        new_col.objects.link(obj)
        
        self.report({'INFO'}, f"Object assigned to '{obj.name}' collection")
    
    def execute(self, context):
        self.quick_collection(context)
        return {'FINISHED'}
    
    
class TOOL_OT_clean_up(bpy.types.Operator):
    bl_idname = "scene.clean_up"
    bl_label = "Clean Up"
    bl_description = "Quickly clean up scene and/or unused data"
    bl_options = {'UNDO'}
    
    action: EnumProperty(
        name = "Cleanup Type",
        description = "Choose what to clean",
        items = [
            ('FILE', "File", "Wipe scene and unused data"),
            ('SCENE', "Scene", "Delete all visible scene objects"),
            ('DATA', "Data", "Delete unused data only"),
            ('MATERIAL', "Material", "Delete all scene materials"),
        ]
    )      
    
    def scene_clean_up(self, context, action):
        # Force Object Mode before running
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        if action == 'FILE':
            for obj in list(bpy.data.objects):
                bpy.data.objects.remove(obj)
            for col in list(bpy.data.collections):
                bpy.data.collections.remove(col)
                
        if action == 'SCENE':
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            
        if action in {'FILE', 'DATA'}:
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            
        if action == 'MATERIAL':
            for mat in list(bpy.data.materials):
                bpy.data.materials.remove(mat)
            
        self.report({'INFO'}, f"Performed cleanup: {action}")
            
        
    def execute(self, context):
        self.scene_clean_up(context, self.action)
    
        return {'FINISHED'} 
    

class TOOL_OT_custom_transform_orientation(bpy.types.Operator):
    bl_idname = "scene.custom_orientation"
    bl_label = "Custom Transform Orientation"
    bl_description = "New transform orientation from selected face, edge, or vertices"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # Check if mesh object is selected AND and Edit Mode with selection
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            return False
        if context.mode != 'EDIT_MESH':
            return False
        
        return obj.data.total_vert_sel > 0
    
    # Pop up box for renaming, with set default name
    new_name: bpy.props.StringProperty(
        name = "Name",
        description = "Name for new transform orientation",
        default = "My Custom"
    )

    def execute(self, context):
        obj = context.active_object
        if obj.type != 'MESH':
            self.report({'WARNING'}, "No mesh object selected")
            return {'CANCELLED'}
        
        if obj.mode != 'EDIT':
            self.report({'WARNING'}, "Mesh object not in edit mode")
            return {'CANCELLED'}
        
        # Create a list of each type based on selected
        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = [v for v in bm.verts if v.select]
        selected_edges = [e for e in bm.edges if e.select]
        selected_faces = [f for f in bm.faces if f.select]
        
        # Check if any mesh property are selected
        if not (selected_verts or selected_edges or selected_faces):
            self.report({'WARNING'}, "No geometry (verts/edges/faces) selected")
            return {'CANCELLED'}
    
        bpy.ops.transform.create_orientation(name=self.new_name, use=True)
        self.report({'INFO'}, f"Created new orienation: {self.new_name}")
        return {'FINISHED'}
    

class TOOL_OT_delete_custom_orientation(bpy.types.Operator):
    bl_idname = "scene.delete_custom"
    bl_label = "Delete Custom Orientation"
    bl_description = "Delete all user created orientations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        transform_slots = context.scene.transform_orientation_slots
        
        if not transform_slots:
            self.report({'WARNING'}, "No transform orientation slots found")
            return {'CANCELLED'}
        
        # Retrieve built-in transform orientation
        builtin_transforms = [i.identifier for i in bpy.types.TransformOrientationSlot.bl_rna.properties['type'].enum_items]

        # hacky (but the only way) to get the all available transforms
        try:
            context.scene.transform_orientation_slots[0].type = ""
        except Exception as inst:
            transforms = str(inst).split("'")[1::2]

        for transform in transforms:
            if transform in builtin_transforms:
                continue
            transform_slots[0].type = transform
            bpy.ops.transform.delete_orientation()
        return {'FINISHED'}
    
    
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
    
    @classmethod
    def poll(cls, context):
        # Only available IF there is a selected Mesh object
        sel_obj = context.selected_objects
        if not sel_obj:
            return False 
        for obj in sel_obj:
            if obj.type != 'MESH':
                return False
        
        return True
    
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
    

class TOOL_OT_export_origin(bpy.types.Operator):
    """Export any object from the origin of scene while maintaining original position"""
    
    bl_label = "Export From Origin"
    bl_idname = "scene.export_origin"
    bl_options = {"UNDO"}
    
    file_format: EnumProperty(
        name="Export File Format",
        description="Choose what file type to export as",
        items=[
            ('FBX', "FBX", ""),  # noqa
            ('GLB', "GLB", ""),  # noqa
            ('OBJ', "OBJ", ""),  # noqa
        ],
    )
    include_children: BoolProperty(
        name="Include Childrens",
        description="Select whether children objects will be exported alongside selected object",
        default=True
    )
    
    @classmethod
    def poll(cls, context):
        # Only available IF there is a selected Mesh object
        sel_obj = context.selected_objects
        if not sel_obj:
            return False 
        for obj in sel_obj:
            if obj.type != 'MESH':
                return False
        
        return True
   
    def export_at_origin(self, context, file_format="", include_children=True):
        output_folder = context.scene.my_addon_props.export_directory
        
        # Warning if no directory is specified
        if not output_folder:
            self.report({'ERROR'}, "Please select an export directory")
            return {'CANCELLED'}

        # Ensure the output folder exists; create it if it doesn't
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Get the currently selected objects in the Blender scene
        raw_selection = context.selected_objects

        # Check if there are any selected objects
        if not raw_selection:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}
        
        # Identify the root object
        top_level_objects = [
            obj for obj in raw_selection
            if obj.parent not in raw_selection
        ]
        
        # Save the original transformations of selected objects
        original_transforms = {
        obj: (
            obj.location.copy(), 
            obj.rotation_euler.copy(), 
            obj.scale.copy()
            ) 
            for obj in top_level_objects
        }

        # Temporarily reset the transformations to the origin for export
        for obj in top_level_objects:
            obj.location = (0, 0, 0)
            obj.rotation_euler = (0, 0, 0)
            obj.scale = (1, 1, 1)

            # Isolate object selection
            for obj in top_level_objects:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                
                if include_children:
                    for child in obj.children_recursive:
                        child.select_set(True)

                # Set the export file path using the object's name
                export_file_path = os.path.join(output_folder, f"{obj.name}.{file_format.lower()}")

                # Export setting
                if file_format == "FBX":
                    bpy.ops.export_scene.fbx(
                        filepath = export_file_path,
                        use_selection = True           
                    )
                
                elif file_format == "GLB":
                    bpy.ops.export_scene.gltf(
                        filepath = export_file_path,
                        use_selection = True,
                        export_apply = True,
                        export_animation_mode = "NLA_TRACKS"           
                    )
                    
                elif file_format == "OBJ":
                    bpy.ops.wm.obj_export(
                        filepath = export_file_path,
                        export_selected_objects = True           
                    )
                    
                self.report({'INFO'}, f"Exported -{obj.name}- as {file_format}")

            # Restore the original transformations of the objects
            for obj, (location, rotation, scale) in original_transforms.items():
                obj.location = location
                obj.rotation_euler = rotation
                obj.scale = scale
            
            # Reselect the original objects    
            for obj in raw_selection:
                obj.select_set(True)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="File Type:")
        layout.prop(self, "file_format", expand=True)
        row.prop(self, "include_children", expand=True)
        
        my_settings = context.scene.my_addon_props
        layout.prop(my_settings, "export_directory")
        layout.separator()
    
    def execute(self, context):
        self.export_at_origin(context, self.file_format, self.include_children)
        export_dir = context.scene.my_addon_props.export_directory
        return {"FINISHED"}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)           
    

classes = [
            TOOL_OT_quick_collection, 
            TOOL_OT_clean_up,
            TOOL_OT_custom_transform_orientation,
            TOOL_OT_delete_custom_orientation,
            TOOL_OT_auto_bevel_weight,
            TOOL_OT_export_origin,
]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()