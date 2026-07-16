import bpy
import bmesh
import math
import mathutils


def edge_select(user_angle, boundary_select, bev_weight):
    
    current_obj = bpy.context.active_object
    bpy.ops.object.editmode_toggle()
    
    bm = bmesh.from_edit_mesh(current_obj.data)
    
    # Check if bevel weight layers exist, if not create one
    bw_layer = bm.edges.layers.float.get("bevel_weight_edge")
    if bw_layer is None:
        bw_layer = bm.edges.layers.float.new("bevel_weight_edge")
    
    manifold_edges = []
    boundary_edges = []

    # define edge types and group them in list
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            manifold_edges.append(edge)
        else:
            boundary_edges.append(edge)
            
    bm.normal_update()
    
    # compare neighboring faces normal   
    for edges in manifold_edges:
        face_a = edges.link_faces[0]
        face_b = edges.link_faces[1]
        angle_rad = face_a.normal.angle(face_b.normal)
        angle = math.degrees(angle_rad)
        if angle > user_angle:
            edges.select = True
            edges[bw_layer] = bev_weight
    
    # boundary edges are automatically considered sharp        
    for edges in boundary_edges:
        if boundary_select == True:
            edges.select = True
        else:
            edges.select = False          
        edges[bw_layer] = bev_weight

    # push changes back to active Edit Mode session without exiting
    bmesh.update_edit_mesh(current_obj.data)
    # bm.free()
    


edge_select(user_angle=50, boundary_select=True, bev_weight=0.5)