import bpy
import bmesh
from bpy.props import EnumProperty


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
        
        tool.label(text="Clean Up Resources", icon='BRUSH_DATA')
        tool.operator("scene.clean_up", text="Wipe Scene", icon='FILE_BACKUP').action = 'FILE'
        tool.operator("scene.clean_up", text="Clear Viewport", icon='SCENE_DATA').action = 'SCENE'
        tool_row = tool.row()
        tool_row.operator("scene.clean_up", text="Wipe All Material", icon='NODE_MATERIAL').action = 'MATERIAL'
        tool_row.operator("scene.clean_up", text="Purge Data", icon='IMAGE_DATA').action = 'DATA'
        
        tool.label(text="Group Similar Materials", icon='BRUSH_DATA')
        tool.operator("scene.material_cleanup", text="Rename - All", icon='NODE_MATERIAL').selection_mode = 'SCENE'
        tool.operator("scene.material_cleanup", text="Rename - Selected Objects", icon='NODE_MATERIAL').selection_mode = 'SELECTED'
        
        tool.separator(type='LINE')
        tool.label(text="Custom Orientation", icon='ORIENTATION_GIMBAL')
        tool_orient = tool.row()
        tool_orient.operator("scene.custom_orientation", text="New", icon='FILE_NEW')
        tool_orient.operator("scene.delete_custom", text="Delete Custom", icon='TRASH')        
         

class MyTool_Panel_subA(bpy.types.Panel):
        bl_label = "Rendering"
        bl_idname = "mytool_panel_subA"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = 'Personal Tools'
        
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
    