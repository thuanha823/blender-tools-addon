import bpy
import random


class AssignIndex:
        
    max_index = 1400

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



    def assign_selected(self, my_index):
            """Assigned a unique Pass Index values to selected objects"""
            
            # Retrieve the number of selected objects
            selected_objects = bpy.context.selected_objects
            obj_count = len(selected_objects)
            
            print(f"{obj_count} Mesh object(s) selected")
            
            if obj_count == 0:
                print("No mesh selected")
                return 
            else:
                pass_index = my_index

            for obj in selected_objects:
                if obj.type in {'MESH'}:
                    obj.pass_index = pass_index
                    print(f"Object '{obj.name}': Pass Index = {pass_index}")
                else:
                    print("No mesh selected")
                    return
            
            print(f"---Success: Assigned Pass Index values of -{my_index}- to selected Mesh objects")



    def assign_collection(self, my_index):
        """Assigns a unique Pass Index value to all objects inside the active collection"""
        
        # Deselect any selection and search for active collection
        bpy.ops.object.select_all(action='DESELECT')
        active_collection = bpy.context.view_layer.active_layer_collection.collection
        
        # Gather all objects from active collection, skipping any that is not a mesh
        collection_obj = []
        for obj in active_collection.objects:
            if obj.type == 'MESH':
                obj.select_set(True)
                collection_obj.append(obj)
            else:
                print(f"Skipped '{obj.name}': Not a mesh")
            
        obj_count = len(collection_obj)
         
        if obj_count == 0:
            print("No mesh selected")
            return 
        else:
            pass_index = my_index
            # pass_index = self.max_index // obj_count
        
        # Set index for objects inside active collection
        for obj in collection_obj:
            obj.pass_index = pass_index
            print(f"Object '{obj.name}': Pass Index = {pass_index}")
                          
        print(f"---Success: Assigned Pass Index value of -{my_index}- to {len(collection_obj)} Mesh objects in '{active_collection.name}'.")



    def assign_random(self):
        """Assigns evenly distributed random Pass Index values to all objects in the Blender scene."""
        
        # Gather all mesh objects into a list
        mesh_obj = []
        for obj in bpy.context.scene.objects:
            if obj.type in {'MESH'}:
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
        
        # Calculate the step size for even distribution with random value, and offset count
        if object_count == 1:
            step_size = 0
        else:
            step_size = random.randint(1, self.max_index) // (object_count + 1)
        
        # Assign Pass Index values to each object
        for i, obj in enumerate(mesh_obj):
            i += 1
            pass_index = (i * step_size)
            obj.pass_index = pass_index
            print(f"Object '{obj.name}': Pass Index = {pass_index}")
                
        print(f"---Success: Assigned randomize Pass Index values to {object_count} Mesh objects")
        return object_count
    
    
    
    def reset_index(self, object_reset=True, material_reset=True):
        """Clear all existing index value and reset to 0"""
        
        # Gather all mesh objects into a list
        mesh_obj = []
        for obj in bpy.context.scene.objects:
            mesh_obj.append(obj)  
        object_count = len(mesh_obj)
        
        # Check if object count exceeds 1000
        if object_count > self.max_index:
            raise ValueError(f"Object count ({object_count}) exceeds maximum limit of 1000")
        
        # Handle edge case of no objects
        if object_count == 0:
            print("No objects found in the scene")
            return 0
        
        # Calculate the step size for even distribution with random value, and offset count
        step_size = 0
        
        # Assign Pass Index values to each object
        for i, obj in enumerate(mesh_obj):
            i += 1
            pass_index = (i * step_size)
        
            if object_reset == True:
                obj.pass_index = pass_index
            elif material_reset == True:
                for slot in obj.material_slots:
                    if slot.material:
                        slot.material.pass_index = pass_index              
              
        if object_reset == True and material_reset == True: 
            print(f"---Successfully reset all Pass Index values to 0 for {object_count} Mesh objects")
        elif object_reset == True and material_reset == False:  
            print(f"---Successfully reset Object Pass Index values to 0 for {object_count} Mesh objects")
        elif object_reset == False and material_reset == True:        
            print(f"---Successfully reset Material Pass Index values to 0 for {object_count} Mesh objects")
        
        return object_count
    



# Testing
objects = AssignIndex()
#objects.assign_material()
#objects.assign_selected(30)
#objects.assign_collection(250)
#objects.assign_random()
#objects.reset_index()


