import bpy 


# 1. Fetch the internal text block named "Protex_index_assign_logic.py" and load it as a module
logic_module = bpy.data.texts["tool_index_assign_logic.py"].as_module()

# 2. Extract your class (AssignIndex) from that module
AssignIndex = logic_module.AssignIndex



class ProtexIndexAssignMaterials(bpy.types.Operator):
    """Iterate through all objects in scene and evenly distribute and assign a unique index value"""
    
    bl_idname = "protex.index_materials"
    bl_label = "Materials"
    bl_description = "Assign each material a unique index"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        manager = AssignIndex()
        manager.assign_material()
        
        material_count = manager.assign_material()
        self.report({'INFO'}, f"Index assigned to {material_count} material(s) in scene")
        return {'FINISHED'}
    
    
    
    
class ProtexIndexAssignObjects(bpy.types.Operator):
    """Assign each objects a random or custom index based on various selection method"""
    
    bl_idname = "protex.index_objects"
    bl_label = "Objects Index Options"
    bl_description = "Assign pass index to objects based on condition"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Properties being used
    set_index: bpy.props.IntProperty(
        name = "Set Index",
        description = "Apply custom index", 
        min = 0, 
        default = 0
    )
    auto_assign: bpy.props.BoolProperty(
        name = "Auto", 
        description="Automatically assigned a random index",
        default = True
    )
    affect_child: bpy.props.BoolProperty(
        name = "Include Child Collection",
        description = "Determine whether objects inside children collection will be affected or not", 
        default = True
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
        layout.label(text="Select target:")
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
            obj_count = manager.assign_selected(self.set_index, self.auto_assign)
            self.report({'INFO'}, f"Index assigned to {obj_count} selected object(s)")
            
        elif self.select_mode == 'COLLECTION':
            active_collection, obj_count = manager.assign_collection(self.set_index, self.auto_assign)
            self.report({'INFO'}, f"Index assigned to {obj_count} objects in '{active_collection.name}' collection")
            
        elif self.select_mode == 'RANDOM':
            obj_count = manager.assign_random()
            self.report({'INFO'}, f"Random Index assigned to {obj_count} object(s)")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    
    

class ProtexResetIndex(bpy.types.Operator):
    """Reset objects/materials index of objects in scene based on various method"""
    
    bl_idname = "protex.index_reset"
    bl_label = "Reset Index Options"
    bl_description = "Reset objects/materials index"
    bl_options = {'REGISTER', 'UNDO'}
    
    object_reset: bpy.props.BoolProperty(
        name = "Object Index",
        description = "Object Pass Index", 
        default=True
    )
    material_reset: bpy.props.BoolProperty(
        name = "Material Index", 
        description = "Material Pass Index", 
        default=True
    ) 
    target_mode : bpy.props.EnumProperty(
        name = "Select Mode",
        description = "Target mode",
        items = [ 
            ('Scene', "Scene", "Reset all objects in scene"),
            ('Selected', "Selection", "Reset selected objects"),
            ('Collection', "Active Collection", "Reset all objects inside active collection")
        ]
    )
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Select target:")
        layout.prop(self, "target_mode", icon='MATERIAL', expand=True)
        layout.separator(type='LINE')
        
        row = layout.row(align=True)
        row.prop(self, "object_reset", toggle=True, icon='MESH_DATA')
        row.prop(self, "material_reset", toggle=True, icon='MATERIAL')
        layout.separator(type='LINE')
        layout.scale_y = 1.1
       
    def execute(self, context):
        manager = AssignIndex()
        active_collection, obj_count = manager.reset_index(
            self.object_reset, 
            self.material_reset, 
            self.target_mode
        )
        
        # Report to user based on various selection
        reset_type = ''
        if self.object_reset and self.material_reset:
            reset_type = 'Objects and Material'
        elif self.object_reset:
            reset_type = 'Objects'
        elif self.material_reset:
            reset_type = 'Material'
        else:
            reset_type = 'None'
        
        if self.target_mode == 'Scene': 
            self.report({'INFO'}, f"{reset_type} Index cleared for {obj_count} object(s) in Scene")
        elif self.target_mode == 'Selected':
            self.report({'INFO'}, f"{reset_type} Index cleared for {obj_count} selected object(s)")
        elif self.target_mode == 'Collection':
            self.report({'INFO'}, f"{reset_type} Index cleared for {obj_count} object(s) in '{active_collection.name}' collection")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

        


class ProtexAssignIndexPanel(bpy.types.Panel):
    bl_label = "Protex Tools"
    bl_idname = "ProtexAssignIndexPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom"
    
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
            ProtexIndexAssignMaterials,
            ProtexIndexAssignObjects,
            ProtexResetIndex,
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
    