import bpy
import bmesh
from bpy.props import EnumProperty

scale_ui = 1.1

# Fetch the internal text block and load it as a module (Testing in Blender)
generalTool_module = bpy.data.texts["general_tools.py"].as_module()
mirrorTool_module = bpy.data.texts["mirror_tool.py"].as_module()
bevelTool_module = bpy.data.texts["Bevel_weight_by_Angle.py"].as_module()
exportTool_module = bpy.data.texts["zero_export_tool.py"].as_module()


class MyTool_Panel(bpy.types.Panel):
    bl_label = "General"
    bl_idname = "mytool_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Personal Tools'
    
    def draw(self, context):
        layout = self.layout
        tool = layout.box()
        tool.label(text="Workflow", icon='TOOL_SETTINGS')
        tool.operator("object.quick_collection", text="Quick Collection", icon='COLLECTION_NEW')
        tool.operator("object.quick_mirror", text="Quick Mirror", icon='MOD_MIRROR')
        tool.operator("object.auto_bevel_weight", text="Auto Bevel Weight", icon='EDGE_BEVEL')
        tool.operator("scene.export_origin", text="Export at Origin", icon='EXPORT')
        tool.separator(type='LINE')
        
        tool.label(text="Clean Up", icon='BRUSH_DATA')
        tool.operator("scene.clean_up", text="File", icon='FILE_BACKUP').action = 'FILE'
        tool.operator("scene.clean_up", text="Material", icon='NODE_MATERIAL').action = 'MATERIAL'
        tool_row = tool.row()
        tool_row.operator("scene.clean_up", text="Scene", icon='SCENE_DATA').action = 'SCENE'
        tool_row.operator("scene.clean_up", text="Data", icon='IMAGE_DATA').action = 'DATA'
        tool.separator(type='LINE')
        
        tool.label(text="Custom Orientation", icon='ORIENTATION_GIMBAL')
        tool.operator("scene.custom_orientation", text="New Orientation", icon='FILE_NEW')
        tool.operator("scene.delete_custom", text="Delete All Custom", icon='TRASH')
        
        
         

class MyTool_Panel_subA(bpy.types.Panel):
        bl_label = "Rendering"
        bl_idname = "mytool_panel_subA"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = 'Personal Tools'
        #bl_parent_id = "mytool_panel"
        
        def draw(self, context):
            layout = self.layout
            index_tool = layout.box()
            index_tool.label(text="Index Assign", icon='PRESET_NEW')
            row = index_tool.row()
            row.operator("object.index_materials", icon='MATERIAL_DATA', text="Materials")
            row.operator("object.index_objects", icon='OBJECT_DATAMODE', text="Objects")
            index_tool.separator(type='LINE')
            index_tool.operator("object.index_reset", icon='FILE_REFRESH', text="Reset Pass Index")

classes = [
            MyTool_Panel,
            MyTool_Panel_subA,
]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()
    