import bpy 


# 1. Fetch the internal text block named "Protex_index_assign_logic.py" and load it as a module
logic_module = bpy.data.texts["tool_index_assign_logic.py"].as_module()

# 2. Extract your class (AssignIndex) from that module
AssignIndex = logic_module.AssignIndex



class VIEW3D_OT_index_assign_materials(bpy.types.Operator):
    bl_idname = "index.assign_materials"
    bl_label = "Materials"
    bl_description = "Assign each material a unique index"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        manager = AssignIndex()
        manager.assign_material()
        return {'FINISHED'}
    
    
    
class VIEW3D_OT_index_assign_selected(bpy.types.Operator):
    bl_idname = "index.assign_selected"
    bl_label = "Selected Objects"
    bl_description = "Assign a unique index to selected mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    set_index: bpy.props.IntProperty(name = "Set Index", default = 0 )
        
    def execute(self, context):
        manager = AssignIndex()
        manager.assign_selected(self.set_index)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



class VIEW3D_OT_index_assign_collection(bpy.types.Operator):
    bl_idname = "index.assign_collection"
    bl_label = "Active Collection"
    bl_description = "Assign a unique index to active collection"
    bl_options = {'REGISTER', 'UNDO'}
       
    set_index: bpy.props.IntProperty(name = "Set Index", default = 0 )   
        
    def execute(self, context):
        manager = AssignIndex()
        manager.assign_collection(self.set_index)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
  
    
    
class VIEW3D_OT_index_assign_random(bpy.types.Operator):
    bl_idname = "index.assign_random"
    bl_label = "Randomize"
    bl_description = "Assign a random index to all mesh in scene"
    bl_options = {'REGISTER', 'UNDO'}
      
    def execute(self, context):
        manager = AssignIndex()
        manager.assign_random()
        return {'FINISHED'}
    
    

class VIEW3D_OT_index_reset(bpy.types.Operator):
    bl_idname = "index.reset"
    bl_label = "Reset"
    bl_description = "Reset index of objects and/or materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    object_reset: bpy.props.BoolProperty(default=True)
    material_reset: bpy.props.BoolProperty(default=True)
       
    def execute(self, context):
        manager = AssignIndex()
        manager.reset_index(self.object_reset, self.material_reset)
        return {'FINISHED'}



'''
# Parent panel
class VIEW3D_PT_parent_panel(bpy.types.Panel):
    bl_label = "Parent Panel"
    bl_idname = "VIEW3D_PT_parent_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Custom'

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is the main panel.")
'''        
        


class VIEW3D_PT_index_assign(bpy.types.Panel):
    bl_label = "Protex Tools"
    bl_idname = "VIEW3D_PT_index_assign"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom"
    # bl_parent_id = "VIEW3D_PT_parent_panel" 
    
    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Index Assign")
        # layout.prop(obj, "pass_index", text="Object Index")
        # layout.separator()
    
        index_tool = layout.box()
        
        index_tool.label(text="Material Index", icon='TOOL_SETTINGS')
        index_tool.operator("index.assign_materials", icon='MATERIAL_DATA', text="Materials")
        index_tool.separator(type='LINE')
        
        index_tool.label(text="Object Index", icon='TOOL_SETTINGS')
        index_tool.operator("index.assign_selected", icon='SELECT_SUBTRACT', text="Selected Objects")
        index_tool.operator("index.assign_collection", icon='OUTLINER_COLLECTION', text="Active Collection")
        index_tool.operator("index.assign_random", icon='CON_TRANSFORM_CACHE', text="Randomize")
        index_tool.separator(type='LINE')
        
        index_tool.label(text="Reset", icon='PRESET')
        btn_all = index_tool.operator("index.reset", icon='LOOP_BACK', text="All Pass Index")
        btn_all.object_reset = True
        btn_all.material_reset = True
        row = index_tool.row()
        btn_obj = row.operator("index.reset", icon='LOOP_BACK', text="Object Index")
        btn_obj.object_reset = True
        btn_obj.material_reset = False
        btn_mtrl = row.operator("index.reset", icon='LOOP_BACK', text="Material Index")
        btn_mtrl.object_reset = False
        btn_mtrl.material_reset = True
        
        
    
classes = [
            VIEW3D_OT_index_assign_materials,
            VIEW3D_OT_index_assign_selected,
            VIEW3D_OT_index_assign_collection,
            VIEW3D_OT_index_assign_random,
            VIEW3D_OT_index_reset,
            VIEW3D_PT_index_assign
            ]  
  
    
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)
    
if __name__ == "__main__":
    register()
    