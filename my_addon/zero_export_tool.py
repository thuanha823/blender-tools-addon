import bpy
import os

def export_at_origin():
    # Specify the output folder for the GLB file
    # Use a raw string to avoid issues with backslashes in file paths
    # output_folder = r"C:\Users\vn57por\Desktop\Sofa Geometry Node\assets\variants_v4"
    output_folder = r"G:\My Drive\Python\Asset"

    # Ensure the output folder exists; create it if it doesn't
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get the currently selected objects in the Blender scene
    selected_objects = bpy.context.selected_objects

    # Check if there are any selected objects
    if not selected_objects:
        print("No objects selected. Please select object(s) to proceed.")
    else:
        # Save the original transformations of selected objects
        original_transforms = {obj: (obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy()) for obj in selected_objects}

        # Temporarily reset the transformations to the origin for export
        for obj in selected_objects:
            obj.location = (0, 0, 0)
            obj.rotation_euler = (0, 0, 0)
            obj.scale = (1, 1, 1)

        # Deselect all objects in the scene
        bpy.ops.object.select_all(action='DESELECT')

        # Reselect the objects that were initially selected
        for obj in selected_objects:
            obj.select_set(True)

        # Export each selected object individually
        for obj in selected_objects:
            # Set the export file path using the object's name
            export_file_path = os.path.join(output_folder, f"{obj.name}.fbx")

            # Export the object to a GLB file with specified settings
            bpy.ops.export_scene.fbx(
                filepath=export_file_path           
            )

            # Notify the user of the successful export for this object
            print(f"Exported {obj.name} to {export_file_path}")

        # Restore the original transformations of the objects
        for obj, (location, rotation, scale) in original_transforms.items():
            obj.location = location
            obj.rotation_euler = rotation
            obj.scale = scale

        # Notify the user that all exports are complete
        print("All selected objects have been exported.")



class OriginExport(bpy.types.Operator):
    """Export any object from the origin of scene while maintaining original position"""
    
    bl_label = "Export From Origin"
    bl_idname = "tool.export_origin"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        export_at_origin("")
        
        return {"FINISHED"}
    
    
classes = [OriginExport]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)
    
if __name__ == "__main__":
    register()
    
