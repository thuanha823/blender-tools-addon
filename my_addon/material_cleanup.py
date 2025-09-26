import bpy
from bpy.props import StringProperty, EnumProperty, FloatProperty

# 1- Access every material on every object
# Loop through all objects in scene, then loop through all material slots of each objects

# 2- Identify the "Duplicate" materials
# Use store current material name, and use split() to separate suffix. Check for valid base name

# 3- Find the original base material
# Retrieve base material name after splitting suffix

# 4- Perform the swap
# Swap any material with suffix to base material


def Material_cleanup(mode):
    delimiter = "."
    to_be_replaced = set()
    total_replacements = 0
    
    if mode == 'All':
        objects_to_process = bpy.context.scene.objects
    elif mode == 'Selected':
        objects_to_process = bpy.context.selected_objects
    else:
        return "Error: Invalid mode"
    
    for obj in objects_to_process:
        if obj.type != 'MESH' or not obj.material_slots:
            continue
        
        for mat in obj.material_slots:
            current_mat = mat.name
            split_str = current_mat.split(delimiter)
            base_mat_name = split_str[0]
            base_material = bpy.data.materials.get(base_mat_name)
            
            if len(split_str) > 1 and split_str[1].isdigit():
                mat.material = base_material
                print(f"{current_mat} replaced with -{base_mat_name}-")
            else:
                print("No changes needed")




class MAT_OT_material_cleanup(bpy.types.Operator):
    bl_idname = "material.mat_cleanup"
    bl_label = "Material Clean Up"
    bl_description = "Replaced any material with suffix with an existing base material"
    bl_options = {'REGISTER', 'UNDO'}
    
    selection_mode: bpy.props.EnumProperty(
        name="mode",
        description="Choose what will be affected by the tool",
        items=[
            ('ALL', 'All', 'Clean up all objects in scene'),
            ('SELECTED', 'Selected', 'Clean up only selected objects in scene')
            ]
        )
    
    def execute(self, context):
        mode = self.selection_mode
        
        if mode == "ALL":
            Material_cleanup("All")
            self.report({'INFO'}, "All scene objects")
        elif mode == "SELECTED":
            Material_cleanup("Selected")
            self.report({'INFO'}, "Selected objects only")
        else:
            self.report({'INFO'}, "Error")
            
        return{'FINISHED'}
    

class MAT_PT_material_cleanup(bpy.types.Panel):
    bl_label = "Material Cleanup"
    bl_idname = "MATERIAL_PT_cleanup"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        operation = row.operator("material.mat_cleanup", text="Cleanup - All")
        operation.selection_mode = "ALL"
        row = layout.row()
        operation = row.operator("material.mat_cleanup", text="Cleanup - Selected")
        operation.selection_mode = "SELECTED"
    

classes = [
            MAT_OT_material_cleanup, 
            MAT_PT_material_cleanup
            ]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)
    
if __name__ == "__main__":
    register()
    