import bpy
from bpy.props import EnumProperty


class VIEW3D_OT_quick_collection(bpy.types.Operator):
    bl_idname = "object.quick_collection"
    bl_label = "Quick Collection"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Create a new collection and name after active object"
    
    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}
        
        collection_name = obj.name
        new_col = bpy.data.collections.new(collection_name)
        context.scene.collection.children.link(new_col)
        
        for col in obj.users_collection:
            col.objects.unlink(obj)
        new_col.objects.link(obj)
        
        self.report({'INFO'}, "Object assigned to collection")
        
        return {'FINISHED'}
    
    
class VIEW3D_OT_clean_up(bpy.types.Operator):
    bl_idname = "view3d.clean_up"
    bl_label = "Clean Up"
    bl_description = "Clean up scene, file, or data"
    bl_options = {'REGISTER', 'UNDO'}
    
    action: EnumProperty(
        name = "Cleanup Type",
        description = "Choose what to clean",
        items = [
            ('FILE', "File", "Delete all objects and purge unused data"),
            ('SCENE', "Scene", "Delete all scene objects"),
            ('DATA', "Data", "Purge unused data only")
        ]
    )      
    
    def execute(self, context):
        if self.action in {'FILE', 'SCENE'}:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            
        if self.action in {'FILE', 'DATA'}:
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            
        self.report({'INFO'}, f"Performed cleanup: {self.action}")
        return {'FINISHED'} 
    

class VIEW3D_OT_custom_transform_orientation(bpy.types.Operator):
    bl_idname = "view3d.custom_orientation"
    bl_label = "Custom Transform Orientation"
    bl_description = "New transform orientation from selected face, edge, or vertices"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Pop up box for renaming, with set default name
    new_name: bpy.props.StringProperty(
        name = "Orientation Name",
        description = "Name for the new transform orientation",
        default = "My Custom"
    )


    def execute(self, context):

        obj = context.active_object
        if obj.type != 'MESH':
            self.report({'WARNING'}, "No mesh object selected")
            return {'CANCELLED'}
        
        if obj.mode != 'EDIT':
            self.report({'WARNING'}, "Mesh object not in edit mode")
            return {'CANCELLED'}
        
        # Create a list of each type based on selected
        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = [v for v in bm.verts if v.select]
        selected_edges = [e for e in bm.edges if e.select]
        selected_faces = [f for f in bm.faces if f.select]
        
        # Check if any mesh property are selected
        if not (selected_verts or selected_edges or selected_faces):
            self.report({'WARNING'}, "No geometry (verts/edges/faces) selected")
            return {'CANCELLED'}
    
        bpy.ops.transform.create_orientation(name=self.new_name, use=True)
        self.report({'INFO'}, f"Created new orienation: {self.new_name}")
        return {'FINISHED'}
    

class VIEW3D_OT_delete_custom_orientation(bpy.types.Operator):
    bl_idname = "view3d.delete_custom"
    bl_label = "Delete Custom Orientation"
    bl_description = "Delete all user created orientations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        transform_slots = context.scene.transform_orientation_slots
        
        if not transform_slots:
            self.report({'WARNING'}, "No transform orientation slots found")
            return {'CANCELLED'}
        
        # Retrieve built-in transform orientation
        builtin_transforms = [i.identifier for i in bpy.types.TransformOrientationSlot.bl_rna.properties['type'].enum_items]

        # hacky (but the only way) to get the all available transforms
        try:
            context.scene.transform_orientation_slots[0].type = ""
        except Exception as inst:
            transforms = str(inst).split("'")[1::2]

        for transform in transforms:
            if transform in builtin_transforms:
                continue
            transform_slots[0].type = transform
            bpy.ops.transform.delete_orientation()
        return {'FINISHED'}
    

class VIEW3D_OT_mirror_object(bpy.types.Operator):
    bl_idname = "view3d.mirror_obj"
    bl_label = "Create Mirror Copy"
    bl_description = "Mirror selected object and create a separate mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    action: EnumProperty(
        name = "Mirror Axis",
        description = "Choose which axis to mirror object across",
        items=[
            ('X', "X", "Mirro X-axis"),
            ('Y', "Y", "Mirro Y-axis"),
            ('Z', "Z", "Mirro Z-axis")
        ], 
        default = 'X'
    )      
    
    def execute(self, context):
        obj = context.active_object
        
        if self.action == 'X':
            pass
        elif self.action == 'Y':
            pass
        elif self.action == 'Z':
            pass
        
        return{'FINISHED'}
    

classes = [
            VIEW3D_OT_quick_collection, 
            VIEW3D_OT_clean_up,
            VIEW3D_OT_custom_transform_orientation,
            VIEW3D_OT_delete_custom_orientation,
]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()