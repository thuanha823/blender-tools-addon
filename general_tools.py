import bpy
import bmesh
from bpy.props import EnumProperty


class TOOL_OT_quick_collection(bpy.types.Operator):
    bl_idname = "object.quick_collection"
    bl_label = "Quick Collection"
    bl_options = {'UNDO'}
    bl_description = "Create a new collection and name after active object"
    
    @classmethod
    def poll(cls, context):
        """The button will only be clickable IF there is an active object"""
        return context.active_object is not None
    
    def quick_collection(self, context):
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
        
        self.report({'INFO'}, f"Object assigned to '{obj.name}' collection")
    
    def execute(self, context):
        self.quick_collection(context)
        return {'FINISHED'}
    
    
class TOOL_OT_clean_up(bpy.types.Operator):
    bl_idname = "scene.clean_up"
    bl_label = "Clean Up"
    bl_description = "Clean up scene, file, or data"
    bl_options = {'UNDO'}
    
    action: EnumProperty(
        name = "Cleanup Type",
        description = "Choose what to clean",
        items = [
            ('FILE', "File", "Wipe scene and unused data"),
            ('SCENE', "Scene", "Delete all visible scene objects"),
            ('DATA', "Data", "Delete unused data only"),
            ('MATERIAL', "Material", "Delete all scene materials"),
        ]
    )      
    
    def scene_clean_up(self, context, action):
        # Force Object Mode before running
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        if action == 'FILE':
            for obj in list(bpy.data.objects):
                bpy.data.objects.remove(obj)
            for col in list(bpy.data.collections):
                bpy.data.collections.remove(col)
                
        if action == 'SCENE':
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            
        if action in {'FILE', 'DATA'}:
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            
        if action == 'MATERIAL':
            for mat in list(bpy.data.materials):
                bpy.data.materials.remove(mat)
            
        self.report({'INFO'}, f"Performed cleanup: {action}")
            
        
    def execute(self, context):
        self.scene_clean_up(context, self.action)
    
        return {'FINISHED'} 
    

class TOOL_OT_custom_transform_orientation(bpy.types.Operator):
    bl_idname = "scene.custom_orientation"
    bl_label = "Custom Transform Orientation"
    bl_description = "New transform orientation from selected face, edge, or vertices"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # Check if mesh object is selected AND and Edit Mode with selection
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            return False
        if context.mode != 'EDIT_MESH':
            return False
        
        return obj.data.total_vert_sel > 0
    
    # Pop up box for renaming, with set default name
    new_name: bpy.props.StringProperty(
        name = "Name",
        description = "Name for new transform orientation",
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
    

class TOOL_OT_delete_custom_orientation(bpy.types.Operator):
    bl_idname = "scene.delete_custom"
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
    

classes = [
            TOOL_OT_quick_collection, 
            TOOL_OT_clean_up,
            TOOL_OT_custom_transform_orientation,
            TOOL_OT_delete_custom_orientation,
]
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()