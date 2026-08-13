import bpy
import os
from bpy.props import EnumProperty
from bpy_extras.io_utils import ExportHelper



class ExportAtOrigin(bpy.types.Operator):
    """Export any object from the origin of scene while maintaining original position"""
    
    bl_label = "Export From Origin"
    bl_idname = "tool.export_origin"
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
    
    @classmethod
    def poll(cls, context):
        # Only available IF there is an active object AND it's a Mesh
        return context.active_object is not None and context.active_object.type == 'MESH'
   
    def export_at_origin(self, context, format):
        output_folder = context.scene.my_addon_props.export_directory
        
        # Warning if no directory is specified
        if not output_folder:
            self.report({'ERROR'}, "Please select an export directory")
            return {'CANCELLED'}

        # Ensure the output folder exists; create it if it doesn't
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Get the currently selected objects in the Blender scene
        selected_objects = context.selected_objects

        # Check if there are any selected objects
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}
        else:
            # Save the original transformations of selected objects
            original_transforms = {
            obj: (
                obj.location.copy(), 
                obj.rotation_euler.copy(), 
                obj.scale.copy()
                ) 
                for obj in selected_objects
            }

            # Temporarily reset the transformations to the origin for export
            for obj in selected_objects:
                obj.location = (0, 0, 0)
                obj.rotation_euler = (0, 0, 0)
                obj.scale = (1, 1, 1)

            # Isolate object selection
            for obj in selected_objects:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)

                # Set the export file path using the object's name
                export_file_path = os.path.join(output_folder, f"{obj.name}.{format}")

                # Export setting
                if format == "FBX":
                    bpy.ops.export_scene.fbx(
                        filepath = export_file_path,
                        use_selection = True           
                    )
                    self.report({'INFO'}, f"Exported {obj.name} as FBX")
                
                elif format == "GLB":
                    bpy.ops.export_scene.gltf(
                        filepath = export_file_path,
                        use_selection = True,
                        export_apply = True,
                        export_animation_mode = "NLA_TRACKS"           
                    )
                    self.report({'INFO'}, f"Exported {obj.name} as GLB")
                    
                elif format == "OBJ":
                    bpy.ops.wm.obj_export(
                        filepath = export_file_path,
                        export_selected_objects = True           
                    )
                    self.report({'INFO'}, f"Exported {obj.name} as OBJ")

            # Restore the original transformations of the objects
            for obj, (location, rotation, scale) in original_transforms.items():
                obj.location = location
                obj.rotation_euler = rotation
                obj.scale = scale
            
            # Reselect the original objects    
            for obj in selected_objects:
                obj.select_set(True)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="File Type:")
        row.prop(self, "file_format", expand=True)
        my_settings = context.scene.my_addon_props
        layout.prop(my_settings, "export_directory")
        layout.separator()
    
    def execute(self, context):
        self.export_at_origin(context, self.file_format)
        export_dir = context.scene.my_addon_props.export_directory
        return {"FINISHED"}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)       

    
classes = [
            ExportAtOrigin,
]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)
    
if __name__ == "__main__":
    register()