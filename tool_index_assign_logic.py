import bpy
import random

from bpy.props import BoolProperty, EnumProperty, FloatProperty, StringProperty, IntProperty

class ProtexIndexAssignMaterials(bpy.types.Operator):
    """Iterate through all objects in scene and evenly distribute and assign a unique index value"""

    bl_idname = "protex.index_materials"
    bl_label = "Materials"
    bl_description = "Assign each material a unique index"
    bl_options = {'UNDO'}

    # Properties being used
    max_index: IntProperty(
        name="Maximum Index",
        description="The maximum value that this tool can assign to any objects",
        default=1400,
    )

    def assign_material(self):
        """Assigns evenly distributed Pass Index values to all materials in the scene."""

        materials = bpy.data.materials
        material_count = len(materials)

        print(f"Found {material_count} materials in the scene")

        # Error flag if material count exceeds max index
        if material_count > self.max_index:
            self.report({'ERROR'}, f"Material count ({material_count}) exceeds maximum limit of {self.max_index}")
            return -1

        # Error flag is no material found in scene
        if material_count == 0:
            print("No materials found in the scene")
            return 0

        # Calculate the step size for even distribution
        if material_count == 1:
            step_size = 0
        else:
            step_size = self.max_index // material_count

        # Assign Pass Index values to each material
        for i, material in enumerate(materials):
            pass_index = i * step_size
            material.pass_index = pass_index
            print(f"Material '{material.name}': Pass Index = {pass_index}")

        print(f"---Success: Assigned Pass Index values to {material_count} materials in scene")
        return material_count

    def execute(self, context):
        material_count = self.assign_material()

        # Safe cancellation if error flag is triggered
        if material_count == -1:
            return {'CANCELLED'}

        self.report({'INFO'}, f"Index assigned to {material_count} material(s) in scene")
        return {'FINISHED'}


class ProtexIndexAssignObjects(bpy.types.Operator):
    """Assign each objects a random or custom index based on various selection method"""

    bl_idname = "protex.index_objects"
    bl_label = "Objects Index Options"
    bl_description = "Assign pass index to objects based on condition"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties being used
    max_index: IntProperty(
        name="Maximum Index",
        description="The maximum value that this tool can assign to any objects",
        default=1400,
    )
    set_index: IntProperty(
        name="Set Index", 
        description="Apply custom index",  
        default=0,
        min=0,
    )
    auto_assign: BoolProperty(
        name="Auto",  # noqa: F821 
        description="Automatically assigned a random index", 
        default=True
    )
    affect_child: BoolProperty(
        name="Include Child Collection",
        description="Determine whether objects inside children collection will be affected or not",
        default=True,
    )
    select_mode: EnumProperty(
        name="Select Mode",
        description="Target mode",
        items=[
            ('SELECTED', "Selection", "New index for objects in selection"),  # noqa
            ('COLLECTION', "Active Collection", "New index for objects in active collection"),  # noqa
            ('RANDOM', "Random", "Randomly assign all objects a unique index"),  # noqa
        ],
    )

    def get_used_indices(self, context):
        """Retrieve all indices that are currently being used in scene"""
        used_index = set()

        # Retrieve and store index
        for obj in context.scene.objects:
            if obj.type == 'MESH' and obj.library is None:
                used_index.add(obj.pass_index)

        return used_index

    def assign_selected(self, context, my_index, auto_assign=False):
        """Assigned a unique Pass Index values to selected objects, either randomized or custom user input"""

        # Retrieve the number of selected mesh objects
        mesh_objects = []
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH' and obj.library is None:
                mesh_objects.append(obj)
        obj_count = len(mesh_objects)

        if obj_count == 0:
            print("No object selected")
            self.report({'WARNING'}, "No object(s) selected")
            return 0

        print(f"{obj_count} Mesh object(s) selected")

        taken_indices = self.get_used_indices(context)

        # Determine how to assign index - user input or random generated
        if auto_assign:
            # If randomly assigned, check if number is taken before assigning. If so keep randomizing until it isn't
            pass_index = random.randint(1, self.max_index)
            while pass_index in taken_indices:
                pass_index = random.randint(1, self.max_index)
            taken_indices.add(pass_index)
        else:
            pass_index = my_index
            taken_indices.add(pass_index)

        # Assign index to selected
        for obj in mesh_objects:
            obj.pass_index = pass_index
            # print(f"Object '{obj.name}': Pass Index = {pass_index}")

        print(f"---Success: Assigned Pass Index values of [{pass_index}] to {obj_count} selected Mesh object(s)")
        return obj_count

    # Idea to improve - Auto distributing to all collection in scene
    def assign_collection(self, context, my_index, auto_assign=False, affect_child=True):
        """Assigns a unique Pass Index value to active collection, with option to apply to children collection"""

        # Deselect any selection and search for active collection
        bpy.ops.object.select_all(action='DESELECT')
        active_collection = bpy.context.view_layer.active_layer_collection.collection

        # Create a set to track all mesh objects within the active collections
        collection_obj = set()
        if affect_child:
            for obj in active_collection.all_objects:
                if obj.type == 'MESH' and obj.library is None:
                    collection_obj.add(obj)
                else:
                    print(f"Skipped '{obj.name}': Not a mesh")
        else:
            for obj in active_collection.objects:
                if obj.type == 'MESH' and obj.library is None:
                    collection_obj.add(obj)
                else:
                    print(f"Skipped '{obj.name}': Not a mesh")

        # Error flag if no objects found inside collection
        obj_count = len(collection_obj)
        if obj_count == 0:
            print(f"No mesh object(s) found in '{active_collection.name}' collection.")
            self.report({'WARNING'}, f"No mesh object(s) found in '{active_collection.name}' collection.")
            return None, 0

        taken_indices = self.get_used_indices(context)

        # Determine how to assign index - user input or random generated
        if auto_assign:
            # If randomly assigned, check if number is taken before assigning. If so keep randomizing until it isn't
            pass_index = random.randint(1, self.max_index)
            while pass_index in taken_indices:
                pass_index = random.randint(1, self.max_index)
            taken_indices.add(pass_index)
        else:
            pass_index = my_index
            taken_indices.add(pass_index)

        # Set index for objects inside active collection
        for obj in collection_obj:
            obj.pass_index = pass_index
            # print(f"Object '{obj.name}': Pass Index = {pass_index}")

        print(
            f"---Success: Assigned Pass Index value to {obj_count} Mesh object(s) in '{active_collection.name}'."
        )
        return active_collection, obj_count

    def assign_random(self, context):
        """Automatically assign randomized Pass Index values to all objects in scene."""

        # Gather all mesh objects into a list
        mesh_obj = []
        for obj in context.scene.objects:
            if obj.type == 'MESH' and obj.library is None:
                mesh_obj.append(obj)

        obj_count = len(mesh_obj)

        print(f"Found {obj_count} Mesh objects in the scene")

        # Error flag if objects count exceeds max index
        if obj_count > self.max_index:
            self.report({'ERROR'}, f"Object count {obj_count} exceeds maximum limit of {self.max_index}")
            return -1

        # Error flag is no objects is found
        if obj_count == 0:
            print("No objects found in the scene")
            self.report({'WARNING'}, "No object(s) found in scene")
            return 0

        # Create a list of entirely unique, non-sequential random integers based on amount of objects in scene
        random_indices = random.sample(range(1, self.max_index + 1), obj_count)

        # Pairs each object with one of the random indices
        for obj, pass_index in zip(mesh_obj, random_indices):
            obj.pass_index = pass_index
            # print(f"Object '{obj.name}': Pass Index = {pass_index}")

        print(f"---Success: Assigned randomize Pass Index values to {obj_count} Mesh object(s)")
        return obj_count

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

        if self.select_mode == 'SELECTED':
            obj_count = self.assign_selected(context, self.set_index, self.auto_assign)
            # Exit if no objects are found
            if obj_count == 0:
                return {'CANCELLED'}
            self.report({'INFO'}, f"Index assigned to {obj_count} selected object(s)")

        elif self.select_mode == 'COLLECTION':
            active_collection, obj_count = self.assign_collection(
                context, self.set_index, self.auto_assign, self.affect_child
            )
            # Exit if no objects are found
            if obj_count == 0:
                return {'CANCELLED'}
            self.report({'INFO'}, f"Index assigned to {obj_count} objects in '{active_collection.name}' collection")

        elif self.select_mode == 'RANDOM':
            obj_count = self.assign_random(context)
            # Exit if no objects are found
            if obj_count == 0:
                return {'CANCELLED'}
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

    # Properties being used
    max_index: IntProperty(
        name="Maximum Index",
        description="The maximum value that this tool can assign to any objects",
        default=1400,
    )
    object_reset: BoolProperty(
        name="Object Index", 
        description="Object Pass Index", 
        default=True
    )
    material_reset: BoolProperty(
        name="Material Index", 
        description="Material Pass Index", 
        default=True
    )
    target_mode: EnumProperty(
        name="Select Mode",
        description="Target mode",
        items=[
            ('Scene', "Scene", "Reset all objects in scene"),  # noqa
            ('Selected', "Selection", "Reset selected objects"),  # noqa
            ('Collection', "Active Collection", "Reset all objects inside active collection"),  # noqa
        ],
    )

    def reset_index(self, object_reset=True, material_reset=True, target_mode=''):
        """Clear all existing index value and reset to 0"""

        if not object_reset and not material_reset:
            return None, 0

        # Gather all mesh objects into a list
        mesh_obj = []

        # Placeholder for potential collection info
        active_collection = None

        # Control how objects data are gather
        if target_mode == 'Scene':
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and obj.library is None:
                    mesh_obj.append(obj)
        elif target_mode == 'Selected':
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                if obj.type == 'MESH' and obj.library is None:
                    mesh_obj.append(obj)
        elif target_mode == 'Collection':
            active_collection = bpy.context.view_layer.active_layer_collection.collection
            for obj in active_collection.all_objects:
                if obj.type == 'MESH' and obj.library is None:
                    mesh_obj.append(obj)

        obj_count = len(mesh_obj)

        # Check if object count exceeds max index, if so return error flag
        if obj_count > self.max_index:
            self.report({'ERROR'}, f"Object count of [{obj_count}] exceeds maximum limit of {self.max_index}")
            return None, -1

        # Handle edge case of no objects in scene
        if obj_count == 0:
            print("No objects found in the scene")
            return None, 0

        # Create a set to remember which materials we've already fixed
        processed_materials = set()

        for obj in mesh_obj:
            # Reset object index
            if object_reset:
                obj.pass_index = 0

            # Reset material index
            if material_reset:
                for slot in obj.material_slots:
                    # Check if there is a material AND if it hasn't been processed
                    if slot.material and slot.material not in processed_materials:
                        slot.material.pass_index = 0
                        processed_materials.add(slot.material)

        # Output messages based on user selection
        if object_reset and not material_reset:
            index_select = 'Object'
        elif not object_reset and material_reset:
            index_select = 'Material'
        elif object_reset and material_reset:
            index_select = 'Object and Material'

        if target_mode == 'Scene':
            target = 'scene'
        elif target_mode == 'Selected':
            target = 'selection'
        elif target_mode == 'Collection':
            target = 'active collection ' + f'"{str(active_collection.name)}"'

        print(f"---Success: Reset {index_select} index for {obj_count} Mesh Object(s) in {target}")

        return active_collection, obj_count

    def draw(self, context):
        layout = self.layout
        layout.label(text="Select target:")
        layout.prop(self, "target_mode", expand=True)
        layout.separator(type='LINE')

        row = layout.row(align=True)
        row.prop(self, "object_reset", toggle=True, icon='MESH_DATA')
        row.prop(self, "material_reset", toggle=True, icon='MATERIAL')
        layout.separator(type='LINE')
        layout.scale_y = 1.1

    def execute(self, context):
        active_collection, obj_count = self.reset_index(self.object_reset, self.material_reset, self.target_mode)

        # Error when objects count exceed max index
        if obj_count == -1:
            return {'CANCELLED'}

        # Warning when no objects are available for selection
        if obj_count == 0:
            self.report({'WARNING'}, "No object(s) were reset.")
            return {'CANCELLED'}

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
            self.report(
                {'INFO'},
                f"{reset_type} Index cleared for {obj_count} object(s) in '{active_collection.name}' collection",
            )

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


classes = [
            ProtexIndexAssignMaterials,
            ProtexIndexAssignObjects,
            ProtexResetIndex,
            ]  
   
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()
    