import bpy 


# 1. Fetch the internal text block named "Protex_index_assign_logic.py" and load it as a module
logic_module = bpy.data.texts["tool_index_assign_logic.py"].as_module()

# 2. Extract your class (AssignIndex) from that module
MaterialIndex = logic_module.ProtexIndexAssignMaterials
ObjectIndex = logic_module.ProtexIndexAssignObjects
ResetIndex = logic_module.ProtexResetIndex



class ProtexAssignIndexPanel(bpy.types.Panel):
    """Create 3 buttons for 3 different main functions, with pop-up dialog box for more options"""
    
    bl_label = "Protex Tools"
    bl_idname = "ProtexAssignIndexPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Index Assign"
    
    def draw(self, context):
        layout = self.layout
        index_tool = layout.box()
        
        index_tool.label(text="Index", icon='LINENUMBERS_ON')
        row = index_tool.row()
        row.operator("protex.index_materials", icon='MATERIAL_DATA', text="Materials")
        row.operator("protex.index_objects", icon='OBJECT_DATAMODE', text="Objects")
        index_tool.separator(type='LINE')
        
        index_tool.label(text="Reset", icon='PRESET')  
        index_tool.operator("protex.index_reset", icon='FILE_REFRESH', text="Reset Pass Index")
        
   
        
    
classes = [
            MaterialIndex,
            ObjectIndex,
            ResetIndex,
            ProtexAssignIndexPanel
            ]  
   
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()
    