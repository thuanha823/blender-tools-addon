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
        
        material_count = manager.assign_material()
        self.report({'INFO'}, f"Index assigned to {material_count} material(s) in scene")
        return {'FINISHED'}
    
    
    
class VIEW3D_OT_index_assign_objects(bpy.types.Operator):
    bl_idname = "index.assign_objects"
    bl_label = "Pass Index Assign"
    bl_description = "Assign pass index to objects"
    bl_options = {'REGISTER', 'UNDO'} # Add Undo support
    
    # Properties being used
    set_index: bpy.props.IntProperty(
        name="Set Index",
        description = "Apply custom index", 
        min=0, 
        default=0
    )
    auto_assign: bpy.props.BoolProperty(
        name="Auto", 
        description="Automatically assigned a random index",
        default = True
    )
    affect_child: bpy.props.BoolProperty(
        name="Include Child Collection",
        description="Determine whether objects inside children collection will be affected or not", 
        default=True
    ) 
    select_mode : bpy.props.EnumProperty(
        name = "Select Mode",
        description = "Target mode",
        items = [ 
            ('SELECTED', "Selection", "New index for objects in selection"),
            ('COLLECTION', "Active Collection", "New index for objects in active collection"),
            ('RANDOM', "Random", "Randomly assign all objects a unique index"),
        ]
    )
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Select your target:")
        layout.prop(self, "select_mode", icon='MATERIAL', expand=True)
        layout.separator(type='LINE')
        
        # Only bring up this menu if in 'COLLECTION' mode
        if self.select_mode == 'COLLECTION':
            layout.prop(self, "affect_child", icon='CON_CHILDOF', expand=True)
        
        # Bring up extra setting for manual input, or random input if not in 'RANDOM' mode
        if self.select_mode != 'RANDOM':
            auto_button = layout.split(factor=0.3)
            auto_button.prop(self, "auto_assign", icon='MATERIAL', toggle=False)
            index_button = auto_button.row()
            
            # Only one options can be enabled at a time
            index_button.enabled = not self.auto_assign
            index_button.prop(self, "set_index", text="Custom Index", icon='MATERIAL')
        layout.separator(type='LINE')
            
        layout.scale_y = 1.1
             
    def execute(self, context):
        manager = AssignIndex()
        if self.select_mode == 'SELECTED':
            manager.assign_selected(self.set_index, self.auto_assign)
            obj_count = manager.assign_selected(self.set_index, self.auto_assign)
            self.report({'INFO'}, f"Index assigned to {obj_count} selected object(s)")
            
        if self.select_mode == 'COLLECTION':
            manager.assign_collection(self.set_index, self.auto_assign, self.affect_child)
            active_collection = manager.assign_collection(self.set_index, self.auto_assign)
            self.report({'INFO'}, f"Index assigned to '{active_collection.name}' collection")
            
        if self.select_mode == 'RANDOM':
            manager.assign_random()
            obj_count = manager.assign_random()
            self.report({'INFO'}, f"Random Index assigned to {obj_count} object(s)")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


'''
class VIEW3D_OT_index_assign_collection(bpy.types.Operator):
    bl_idname = "index.assign_collection"
    bl_label = "Active Collection"
    bl_description = "Assign a unique index to active collection"
    bl_options = {'REGISTER', 'UNDO'}
       
    set_index: bpy.props.IntProperty(name = "Set Index", default = 0)
    auto_assign: bpy.props.BoolProperty(name = "Auto Assign", default = True)   
    affect_child: bpy.props.BoolProperty(name = "Affect Child Collection", default = True) 
        
    def execute(self, context):
        manager = AssignIndex()
        manager.assign_collection(self.set_index, self.auto_assign, self.affect_child)
        
        active_collection = manager.assign_collection(self.set_index, self.auto_assign, self.affect_child)
        self.report({'INFO'}, f"Index assigned to '{active_collection.name}' collection")
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
        
        obj_count = manager.assign_random()
        self.report({'INFO'}, f"Random Index assigned to {obj_count} object(s)")
        return {'FINISHED'}
'''    
    

class VIEW3D_OT_index_reset_scene(bpy.types.Operator):
    bl_idname = "index.reset_scene"
    bl_label = "Reset"
    bl_description = "Reset index of scene objects and/or materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    object_reset: bpy.props.BoolProperty(name = "Object Index", default=True)
    material_reset: bpy.props.BoolProperty(name = "Material Index", default=True)
    target_mode: bpy.props.StringProperty(default='Scene')
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "object_reset", toggle=True, icon='MESH_DATA')
        layout.prop(self, "material_reset", toggle=True, icon='MATERIAL')
       
    def execute(self, context):
        manager = AssignIndex()
        manager.reset_index(self.object_reset, self.material_reset, self.target_mode)
        self.report({'INFO'}, "Index reset to 0")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



class VIEW3D_OT_index_reset_selected(bpy.types.Operator):
    bl_idname = "index.reset_selected"
    bl_label = "Reset"
    bl_description = "Reset index of selected objects and/or materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    object_reset: bpy.props.BoolProperty(name = "Object Index", default=True)
    material_reset: bpy.props.BoolProperty(name = "Material Index", default=True)
    target_mode: bpy.props.StringProperty(default='Selected')
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "object_reset", toggle=True, icon='MESH_DATA')
        layout.prop(self, "material_reset", toggle=True, icon='MATERIAL')
       
    def execute(self, context):
        manager = AssignIndex()
        manager.reset_index(self.object_reset, self.material_reset, self.target_mode)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    
    
class VIEW3D_OT_index_reset_collection(bpy.types.Operator):
    bl_idname = "index.reset_collection"
    bl_label = "Reset"
    bl_description = "Reset index of objects and/or materials in active collection"
    bl_options = {'REGISTER', 'UNDO'}
    
    object_reset: bpy.props.BoolProperty(name="Object Index", default=True)
    material_reset: bpy.props.BoolProperty(name="Material Index", default=True)
    target_mode: bpy.props.StringProperty(default='Collection')
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "object_reset", toggle=True, icon='MESH_DATA')
        layout.prop(self, "material_reset", toggle=True, icon='MATERIAL')
       
    def execute(self, context):
        manager = AssignIndex()
        manager.reset_index(self.object_reset, self.material_reset, self.target_mode)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
       
        



class VIEW3D_PT_index_assign(bpy.types.Panel):
    bl_label = "Protex Tools"
    bl_idname = "VIEW3D_PT_index_assign"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom"
    
    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Index Assign")
        index_tool = layout.box()
        
        index_tool.label(text="Index", icon='TOOL_SETTINGS')
        index_tool.operator("index.assign_materials", icon='MATERIAL_DATA', text="Materials")
        #index_tool.separator(type='LINE')
        
        #index_tool.label(text="Object Index", icon='TOOL_SETTINGS')
        index_tool.operator("index.assign_selected", icon='SELECT_SUBTRACT', text="Objects")
        #index_tool.operator("index.assign_collection", icon='OUTLINER_COLLECTION', text="Active Collection")
        #index_tool.operator("index.assign_random", icon='CON_TRANSFORM_CACHE', text="Randomize")
        #index_tool.separator(type='LINE')
        
        index_tool.label(text="Reset", icon='PRESET')  
        btn_all = index_tool.operator("index.reset_scene", icon='LOOP_BACK', text="All Pass Index")
        btn_all = index_tool.operator("index.reset_selected", icon='LOOP_BACK', text="Selected Objects")
        btn_all = index_tool.operator("index.reset_collection", icon='LOOP_BACK', text="Active Collection")
        
        
    
classes = [
            VIEW3D_OT_index_assign_materials,
            VIEW3D_OT_index_assign_objects,
            #VIEW3D_OT_index_assign_collection,
            #VIEW3D_OT_index_assign_random,
            VIEW3D_OT_index_reset_scene,
            VIEW3D_OT_index_reset_selected,
            VIEW3D_OT_index_reset_collection,
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
    