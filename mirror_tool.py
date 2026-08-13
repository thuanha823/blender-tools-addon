import bpy
import bmesh
from mathutils import Vector



class MirrorObject:
    
    WORLD_ORIGIN = Vector((0.0, 0.0, 0.0))
    
    def __init__(self, axis):
        self.axis = axis
        
    def mirror_obj(self, context):
        """Mirror object across world origin axis"""
        
        obj = context.active_object
        
        # Assign modifier to variable
        mod = obj.modifiers.new(name="Custom Mirror", type="MIRROR")
        
        # Set axis
        mod.use_axis[0] = (self.axis == 'X')
        mod.use_axis[1] = (self.axis == 'Y')
        mod.use_axis[2] = (self.axis == 'Z')

        # Create an empty at world origin without deselecting active object
        mirror_empty = bpy.data.objects.new("Empty_Mirror", None)
        context.collection.objects.link(mirror_empty)
        
        # Assign empty to modifier
        mod.mirror_object = mirror_empty

        # Apply Modifier and delete empty
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(mirror_empty)
        
        return obj


    def separate_obj(self, context):
        """Separate mirrored object from original"""
        
        # Store original object name
        obj = context.active_object
        base_name = obj.name
        
        # Enter Edit Mode safely
        if obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all geometry and separate
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # enter the origins immediately and retrieve location
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        
        # Renaming based on actual physical location
        for selected in context.selected_objects:
            
            # Check the actual coordinate of the centered origin
            if self.axis == 'X':
                suffix = "_r" if selected.location.x > 0 else "_l"
            elif self.axis == 'Y':
                suffix = "_r" if selected.location.y > 0 else "_l"
            elif self.axis == 'Z':
                suffix = "_top" if selected.location.z > 0 else "_bot"
                
            selected.name = base_name + suffix
        
        return obj
        
        
    def center_origin(self, context, origin_setting=""):
        """Set the origin of the merged/separated object"""
        
        if context.active_object and context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        if origin_setting == 'CENTER_WORLD':
            # Retrieve and store 3D cursor location
            cursor = context.scene.cursor
            saved_cursor_loc = cursor.location.copy()
            
            # Move cursor to world origin temporarily and set object origin
            try:
                cursor.location = self.WORLD_ORIGIN
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            finally:
                cursor.location = saved_cursor_loc
                
        elif origin_setting == 'CENTER_OBJECT':
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
    


class ProtexQuickMirror(bpy.types.Operator):
    """Mirror a selected objected across specific axis"""
    
    bl_label = "Quick Mirror"
    bl_idname = "tool.quick_mirror"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        # Only available IF there is an active object AND it's a Mesh
        return context.active_object is not None and context.active_object.type == 'MESH'
    
    axis: bpy.props.EnumProperty(
        name = "Axis",
        items = [
            ('X', "X", "Mirror across X-axis"),
            ('Y', "Y", "Mirror across Y-axis"),
            ('Z', "Z", "Mirror across Z-axis")
        ],
        default = 'X',
        options = set()
    )
    separate_obj: bpy.props.BoolProperty(
        name = "Separate Object",
        description = "Separate meshes after mirroring",
        default = True
    )
    origin_setting: bpy.props.EnumProperty(
        name = "Origin Set Option",
        items = [
            ('CENTER_WORLD', "World", "Snap object origin to world origin"),
            ('CENTER_OBJECT', "Object", "Snap origin to object center")
        ],
        default = 'CENTER_OBJECT',
        options = set()
    )
  
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Mirror Axis")
        layout.prop(self, "axis", icon='MOD_EDGESPLIT', expand=True)
        layout.prop(self, "separate_obj", icon='MOD_EDGESPLIT', expand=True)
        layout.label(text="Center Origin")
        layout.prop(self, "origin_setting", icon='TRANSFORM_ORIGINS', expand=True)
        layout.separator(type='LINE')
        
    
    def execute(self, context):
        tool = MirrorObject(self.axis)
        tool.mirror_obj(context)
        if self.separate_obj:
            tool.separate_obj(context)
        tool.center_origin(context, self.origin_setting)
        
        self.report({'INFO'}, f"Object mirrored acrossed {self.axis}-axis")
        
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)
    
    
    
class ProtexPanelQuickMirror(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_protex_panel_quickMirror"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Thuan\'s Addon"
    bl_label = "Custom Tool"
    
    def draw(self, context):
        layout = self.layout
        mirror_tool = layout.box()  
        row = mirror_tool.row()
        row.operator("tool.quick_mirror", icon="MOD_MIRROR")
    
    

classes = [
            ProtexQuickMirror,
            ProtexPanelQuickMirror
            ]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()
