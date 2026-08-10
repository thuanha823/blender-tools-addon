import bpy
import bmesh
import re
from mathutils import Vector



class MirrorObject:
    def __init__(self, axis):
        self.axis = axis
        
    def mirror_obj(self, context):
        """Mirror object across world origin axis"""
        
        active_obj = bpy.context.active_object
        obj_name = active_obj.name
        obj = bpy.data.objects.get(obj_name)
        
        # assign modifier to variable
        mod = obj.modifiers.new(name="TempName", type="MIRROR")
        mod.name = "Custom Mirror"
        
        # choose which axis to mirror across
        if self.axis == 'X':
            mod.use_axis[0] = True
        elif self.axis == 'Y':
            mod.use_axis[0] = False
            mod.use_axis[1] = True
        elif self.axis == 'Z': 
            mod.use_axis[0] = False
            mod.use_axis[1] = False
            mod.use_axis[2] = True

        # Create an empty at world origin
        bpy.ops.object.empty_add(
            type='CUBE', 
            align='WORLD', 
            location=(0, 0, 0), 
            scale=(1, 1, 1)
        )
        mirror_empty = bpy.context.active_object
        mirror_empty.name = "Empty_Mirror"
        empty_name = mirror_empty.name
        # mirror_empty.hide_set(True)

        # Assign variable to empty
        empty = bpy.data.objects.get(empty_name)
        mod.mirror_object = empty

        # mirror_empty.hide_set(False)
        
        # apply modifier and delete empty 
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(mirror_empty)

        return obj


    def separate_obj(self, context):
        """Separate mirrored object from original"""

        active_obj = bpy.context.active_object
        world_origin = active_obj.location
        obj_name = active_obj.name
        obj = bpy.data.objects.get(obj_name)
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Vert select mode and storing bmesh data
        bm = bmesh.from_edit_mesh(obj.data)
        bpy.ops.mesh.select_mode(type="VERT")
        
        # Select all verts under certain condition
        for verts in bm.verts:
            # Convert vertex local coord into world coord
            world_pos = obj.matrix_world @ verts.co
            
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
        
        # Select all connected faces of selected verts
        for faces in bm.faces:
            for verts in faces.verts:
                if verts.select == True:
                    faces.select = True
                else:
                    faces.select = False
        
        # Update mesh selection and separate
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.object.select_all(action='SELECT')
        
        # Renaming mesh based on location
        for selected in bpy.context.selected_objects:
            # Find the newly created obj
            if selected.name != obj.name:
                print(selected.name)
                new_obj = bpy.data.objects.get(selected.name)
                # Strip away 3 digit following .
                new_obj_name = re.sub(r"\.\d{3}$", "", selected.name)
                if self.axis == 'X' or self.axis == 'Y':
                    new_obj.name = new_obj_name + "_r"
                elif self.axis == 'Z':
                    new_obj.name = new_obj_name + "_top"
            else:
                if self.axis == 'X' or self.axis == 'Y':
                    obj.name = bpy.context.active_object.name + "_l"
                elif self.axis == 'Z':
                    obj.name = bpy.context.active_object.name + "_bot"
              
        #bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
              
        return obj
        
        
    def center_origin():
        pass
    


class ProtexQuickMirror(bpy.types.Operator):
    """Mirror a selected objected across specific axis"""
    
    bl_label = "Quick Mirror"
    bl_idname = "tool.quick_mirror"
    bl_options = {"REGISTER", "UNDO"}
    
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
    origin_set: bpy.props.EnumProperty(
        name = "Origin Set Option",
        items = [
            ('Original', "Keep original", "Maintain original origin location"),
            ('Center =', "Center object", "Set origin to object physical center")
        ],
        default = 'Original',
        options = set()
    )
    
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Mirror Axis")
        layout.prop(self, "axis", icon='MOD_EDGESPLIT', expand=True)
        layout.prop(self, "separate_obj", icon='MOD_EDGESPLIT', expand=True)
        layout.prop(self, "origin_set", icon='TRANSFORM_ORIGINS', expand=True)
        layout.separator(type='LINE')
        
    
    def execute(self, context):
        tool = MirrorObject(self.axis)
        tool.mirror_obj(context)
        if self.separate_obj:
            tool.separate_obj(context)
        if self.origin_set == 'Center':
            pass
        
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)
    
    
    
class ProtexPanelQuickMirror(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_protex_panel_quickMirror"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Thuan\'s Addon"
    bl_label = "General Tool"
    
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
        bpy.utils.register_class(cls)
    
if __name__ == "__main__":
    register()
