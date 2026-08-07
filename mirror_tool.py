import bpy
import bmesh
import re
from mathutils import Vector
from bpy.props import EnumProperty


class MirrorObject:
    def __init__(self, axis=0):
        self.axis = axis
        
    def mirror_obj(self):
        obj_name = bpy.context.active_object.name
        obj = bpy.data.objects.get(obj_name)
        
        # assign modifier to variable
        mod = obj.modifiers.new(name="TempName", type="MIRROR")
        mod.name = "Custom Mirror"
        
        # choose which axis to mirror across
        if self.axis == 0:
            mod.use_axis[0] = True
        elif self.axis == 1:
            mod.use_axis[0] = False
            mod.use_axis[1] = True
        elif self.axis == 2: 
            mod.use_axis[0] = False
            mod.use_axis[1] = False
            mod.use_axis[2] = True

        # Create an empty at world origin
        bpy.ops.object.empty_add(type='CUBE', 
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


    def separate_obj(self):
        obj_name = bpy.context.active_object.name
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
            if self.axis == 0:
                if world_pos.x > 0:
                    verts.select = True    
                else:
                    verts.select = False
            elif self.axis == 1:
                if world_pos.y > 0:
                    verts.select = True    
                else:
                    verts.select = False
            else:
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
        bpy.ops.mesh.separate(type = 'SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        
        # Renaming mesh based on location
        for selected in bpy.context.selected_objects:
            # Find the newly created obj
            if selected.name != obj.name:
                print(selected.name)
                new_obj = bpy.data.objects.get(selected.name)
                # Strip away 3 digit following .
                new_obj_name = re.sub(r"\.\d{3}$", "", selected.name)
                if self.axis == 0 or self.axis == 1:
                    new_obj.name = new_obj_name + "_r"
                elif self.axis == 2:
                    new_obj.name = new_obj_name + "_top"
            else:
                if self.axis == 0 or self.axis == 1:
                    obj.name = bpy.context.active_object.name + "_l"
                elif self.axis == 2:
                    obj.name = bpy.context.active_object.name + "_bottom"

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
              
        return obj
        
    def fix_origin():
        pass



# bpy.ops.mesh.primitive_monkey_add(location=(5, 2, 3))
objects = MirrorObject()
objects.mirror_obj()
objects.separate_obj()


class MirrorMesh(bpy.types.Operator):
    """Mirror a copy of selected objected across specific axis"""
    
    bl_label = "Mirror Mesh"
    bl_idname = "tool.mirror_mesh"
    bl_options = {"REGISTER", "UNDO"}
    
    axis: EnumProperty(
        name = "Axis",
        description = "Axis to mirror across",
        items = [
            ('X', "X", "Reflect along the X-axis"),
            ('Y', "Y", "Reflect along the Y-axis"),
            ('Z', "Z", "Reflect along the Z-axis"),
        ],
        default = 'X',
        options = set(),
    )
    
    def execute(self, context):
        objects = MirrorObject(self.axis)
        objects.mirror_obj()
        objects.separate_obj()
        
        return {"FINISHED"}
    

classes = [MirrorMesh]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)
    
if __name__ == "__main__":
    register()
    



