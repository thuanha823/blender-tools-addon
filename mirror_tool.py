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
            
        # Switch to Vertex mode
        context.tool_settings.mesh_select_mode = (True, False, False)
        
        # Vert select mode and storing bmesh data
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Deselect everything
        for verts in bm.verts: 
            verts.select = False
        for faces in bm.faces: 
            faces.select = False
        
        # Store world matrix outside loop
        world_mtx = obj.matrix_world
        
        # Select all verts under certain condition
        for verts in bm.verts:
            # Convert vertex local coord into world coord
            world_pos = world_mtx @ verts.co
            
            # Define selection for separation based on world location
            if self.axis == 'X':
                if world_pos.x > 0:
                    verts.select = True
                else:
                    verts.select = False
            elif self.axis == 'Y':
                if world_pos.y > 0:
                    verts.select = True
                else:
                    verts.select = False
            elif self.axis == 'Z':
                if world_pos.z > 0:
                    verts.select = True
                else:
                    verts.select = False
        
        # Select face if any vertices is selected
        for faces in bm.faces:
            faces.select = any(verts.select for verts in faces.verts)
        
        # Update mesh selection and separate
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Renaming mesh upon separation
        for selected in bpy.context.selected_objects:
            # Find the newly created obj
            if selected != obj:
                if self.axis in {'X', 'Y'}:
                    selected.name = base_name + "_l"
                elif self.axis == 'Z':
                    selected.name = base_name + "_top"
            else:
                if self.axis in {'X', 'Y'}:
                    selected.name = base_name + "_r"
                elif self.axis == 'Z':
                    selected.name = base_name + "_bot"
              
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
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    


class ProtexQuickMirror(bpy.types.Operator):
    """Mirror a selected objected across specific axis"""
    
    bl_label = "Quick Mirror"
    bl_idname = "tool.quick_mirror"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        # The button will only be clickable IF there is an active object AND it's a Mesh
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
