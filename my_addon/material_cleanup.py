import bpy

# 1- Access every material on every object
# Loop through all objects in scene, then loop through all material slots of each objects

# 2- Identify the "Duplicate" materials
# Use store current material name, and use split() to separate suffix. Check for valid base name

# 3- Find the original base material
# Retrieve base material name after splitting suffix

# 4- Perform the swap
# Swap any material with suffix to base material


def Material_cleanup():
    delimiter = "."
    for obj in bpy.context.scene.objects:
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

        print(f"---{obj.name}---")
        
    return f"Replaced all materials to {base_mat_name}"
        


class MAT_OT_material_cleanup(bpy.types.Operator):
    bl_idname = "material.mat_cleanup"
    bl_label = "Material Clean Up"
    bl_description = "Replaced any material with suffix with an existing base material"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        Material_cleanup()
        report_message = Material_cleanup()
        self.report({'INFO'}, report_message)
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
        row.operator("material.mat_cleanup", text="Cleanup")
    

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
    