import bpy
import bmesh
from bpy.props import EnumProperty

scale_ui = 1.1

# Fetch the internal text block and load it as a module (Testing in Blender)
generalTool_module = bpy.data.texts["general_tools.py"].as_module()
quickCollection = generalTool_module.VIEW3D_OT_quick_collection
cleanUp = generalTool_module.VIEW3D_OT_clean_up
custom_orient = generalTool_module.VIEW3D_OT_custom_transform_orientation
clear_orient = generalTool_module.VIEW3D_OT_delete_custom_orientation

mirrorTool_module = bpy.data.texts["mirror_tool.py"].as_module()
quickMirror = mirrorTool_module.ProtexQuickMirror

bevelTool_module = bpy.data.texts["Bevel_weight_by_Angle.py"].as_module()
bevelTool = bevelTool_module.ProtexAutoBevelWeight

exportTool_module = bpy.data.texts["zero_export_tool.py"].as_module()


class MyTool_Panel(bpy.types.Panel):
    bl_label = "My Tools"
    bl_idname = "mytool_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Thuan\'s Addon'
    
    def draw(self, context):
        layout = self.layout
        tool = layout.box()
        tool.label(text="General Tools", icon='TOOL_SETTINGS')
        tool.operator("object.quick_collection", text="Quick Collection", icon='COLLECTION_NEW')
        tool.operator("tool.quick_mirror", text="Quick Mirror", icon='MOD_MIRROR')
        tool.operator("protex.autobevelweight", text="Auto Bevel Weight", icon='EDGE_BEVEL')
        tool.operator("tool.export_origin", text="Export at Origin", icon='EXPORT')
        tool.separator(type='LINE')
        
        tool.label(text="Clean Up", icon='BRUSH_DATA')
        tool.operator("view3d.clean_up", text="File", icon='FILE_BACKUP').action = 'FILE'
        tool_row = tool.row()
        tool_row.operator("view3d.clean_up", text="Scene", icon='SCENE_DATA').action = 'SCENE'
        tool_row.operator("view3d.clean_up", text="Data", icon='IMAGE_DATA').action = 'DATA'
        tool.separator(type='LINE')
        
        tool.label(text="Custom Orientation", icon='ORIENTATION_GIMBAL')
        tool.operator("view3d.custom_orientation", text="New Orientation")
        tool.operator("view3d.delete_custom", text="Delete All Custom Orientation")
        
        index_tool = layout.box()
        index_tool.label(text="Index Assign", icon='PRESET_NEW')
        row = index_tool.row()
        row.operator("protex.index_materials", icon='MATERIAL_DATA', text="Materials")
        row.operator("protex.index_objects", icon='OBJECT_DATAMODE', text="Objects")
        index_tool.separator(type='LINE')
        index_tool.operator("protex.index_reset", icon='FILE_REFRESH', text="Reset Pass Index")
         

classes = [
            MyTool_Panel,
            cleanUp,
            custom_orient,
            clear_orient,
            quickMirror,
            bevelTool,
]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()
    