import bpy
import random


class AssignIndex:
        
    max_index = 1400
    used_index = set()

    def assign_material(self):    
        """Assigns evenly distributed Pass Index values to all materials in the scene.  """
            
        materials = bpy.data.materials
        material_count = len(materials)
        
        print(f"Found {material_count} materials in the scene")
        
        # Check if material count exceeds 1000
        if material_count > self.max_index:
            raise ValueError(f"Material count ({material_count}) exceeds maximum limit of 1000")
        
        # Handle edge case of no materials
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



    def assign_selected(self, my_index, auto_assign = False):
            """Assigned a unique Pass Index values to selected objects"""
            
            # Retrieve the number of selected mesh objects
            mesh_objects = []
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                if obj.type == 'MESH' and obj.library is None:
                    mesh_objects.append(obj)
            obj_count = len(mesh_objects)
       
            if obj_count == 0:
                print("No object selected")
                return 
            
            print(f"{obj_count} Mesh object(s) selected")
            
            # Determine if user want manual input or randomly assign
            if auto_assign:
                pass_index = random.randint(1, self.max_index)
            else:
                pass_index = my_index
            
            # Add index to set
            self.used_index.add(pass_index)
            
            # Assign index to selected 
            for obj in mesh_objects:
                obj.pass_index = pass_index
                print(f"Object '{obj.name}': Pass Index = {pass_index}")  

            print(f"---Success: Assigned Pass Index values of -{pass_index}- to {obj_count} selected Mesh object(s)")



    # Idea - Potentially auto distributing to all collection in scene
    def assign_collection(self, my_index, auto_assign = False, affect_child = True):
        """Assigns a unique Pass Index value to all objects inside the active collection"""
        
        # Deselect any selection and search for active collection
        bpy.ops.object.select_all(action='DESELECT')
        active_collection = bpy.context.view_layer.active_layer_collection.collection
        
        # Create a set to track all mesh objects within the active collections
        collection_obj = set()
        if affect_child:
            for obj in active_collection.all_objects:
                if obj.type == 'MESH' and obj.library is None:
                    # obj.select_set(True) # Testing
                    collection_obj.add(obj)
                else:
                    print(f"Skipped '{obj.name}': Not a mesh")
        else:
            for obj in active_collection.objects:
                if obj.type == 'MESH' and obj.library is None:
                    # obj.select_set(True) # Testing
                    collection_obj.add(obj)
                else:
                    print(f"Skipped '{obj.name}': Not a mesh")
                   
        obj_count = len(collection_obj)
        if obj_count == 0:
            print(f"No mesh object(s) found in collection '{active_collection.name}' Collection.")
            return 
        
        if auto_assign:
            pass_index = random.randint(1, self.max_index)
        else:
            pass_index = my_index
        
        # Add index to set
        self.used_index.add(pass_index)
        
        # Set index for objects inside active collection
        for obj in collection_obj:
            obj.pass_index = pass_index
            print(f"Object '{obj.name}': Pass Index = {pass_index}")
                          
        print(f"---Success: Assigned Pass Index value of -{pass_index}- to {obj_count} Mesh object(s) in '{active_collection.name}' Collection.")


    # Issue - Could be better distributed, some mesh color blend together within close prox
    def assign_random(self):
        """Assigns evenly distributed random Pass Index values to all objects in the Blender scene."""
        
        # Gather all mesh objects into a list
        mesh_obj = []
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.library is None:
                mesh_obj.append(obj)
                
        object_count = len(mesh_obj)
        
        print(f"Found {object_count} Mesh objects in the scene")
        
        # Check if object count exceeds 1000
        if object_count > self.max_index:
            raise ValueError(f"Object count ({object_count}) exceeds maximum limit of 1000")
        
        # Handle edge case of no objects
        if object_count == 0:
            print("No objects found in the scene")
            return 0
        
        # Create a list of entirely unique, non-sequential random integers based on amount of objects in scene
        random_indices = random.sample(range(1, self.max_index + 1), object_count)
        
        # Pairs each object with one of the random indices
        for obj, pass_index in zip(mesh_obj, random_indices):
            obj.pass_index = pass_index
            print(f"Object '{obj.name}': Pass Index = {pass_index}")
                
        print(f"---Success: Assigned randomize Pass Index values to {object_count} Mesh object(s)")
        return object_count
    
    
    # Ideas - Reset selected objects/ collection only
    def reset_index(self, object_reset=True, material_reset=True):
        """Clear all existing index value and reset to 0"""
        
        if not object_reset and not material_reset:
            return
        
        # Gather all mesh objects into a list
        mesh_obj = []
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.library is None:
                mesh_obj.append(obj)  
        object_count = len(mesh_obj)
        
        # Check if object count exceeds 1000
        if object_count > self.max_index:
            raise ValueError(f"Object count ({object_count}) exceeds maximum limit of 1000")
        
        # Handle edge case of no objects
        if object_count == 0:
            print("No objects found in the scene")
            return
        
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
                        
        # Empty your tracking list
        self.used_index.clear()
                
        if object_reset and not material_reset:
            print(f"---Success: Reset Object Pass Index values for {object_count} Mesh object(s).")
        elif not object_reset and material_reset:
            print(f"---Success: Reset Material Pass Index values for {object_count} Mesh object(s).")
        else:
            print(f"---Success: Reset all Pass Index values for {object_count} Mesh object(s).")

    


#Testing
objects = AssignIndex()
#objects.assign_material()
#objects.assign_selected(my_index = None, auto_assign = True)
#objects.assign_collection(my_index = None, auto_assign = True)
#objects.assign_random()
#objects.reset_index()

