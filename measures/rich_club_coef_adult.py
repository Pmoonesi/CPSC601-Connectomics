import sys
import os
import csv
import snap

def get_rich_club(input_path, output_dir, network_name):
    try:
        G = snap.LoadEdgeList(snap.TNGraph, input_path, 0, 1)
    except Exception as e:
        print(e)
        return

    # rank nodes by total degree
    node_deg_pairs = []
    for NI in G.Nodes():
        node_deg_pairs.append((NI.GetId(), NI.GetDeg()))
    
    node_deg_pairs.sort(key=lambda x: x[1], reverse=True)
    
    club_nodes_set = set()
    club_edge_count = 0
    rich_club_data = [] 
    
    for i in range(len(node_deg_pairs)):
        curr_nid, curr_deg = node_deg_pairs[i]
        curr_node = G.GetNI(curr_nid)
        
        # count out edges to existing club
        for j in range(curr_node.GetOutDeg()):
            if curr_node.GetOutNId(j) in club_nodes_set:
                club_edge_count += 1
                
        # count in edges to existing club
        for j in range(curr_node.GetInDeg()):
            nbr = curr_node.GetInNId(j)
            if nbr != curr_nid and nbr in club_nodes_set:
                club_edge_count += 1
                
        # add to club
        club_nodes_set.add(curr_nid)
        
        # save coefficient
        is_last = (i == len(node_deg_pairs) - 1)
        next_deg = -1 if is_last else node_deg_pairs[i+1][1]
        
        if is_last or (curr_deg > next_deg):
            k_threshold = curr_deg - 1
            if k_threshold < 1: continue
                
            n_club = len(club_nodes_set)
            if n_club > 1:
                max_edges = n_club * (n_club - 1) # possible directed 
                phi = float(club_edge_count) / max_edges
                rich_club_data.append([k_threshold, phi, n_club, club_edge_count])

    curve_filename = f"{network_name}_rich_club_curve.csv"
    curve_path = os.path.join(output_dir, curve_filename)
    
    with open(curve_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['k', 'phi', 'n_club', 'e_club'])
        for row in reversed(rich_club_data):
            writer.writerow(row)
                
if len(sys.argv) < 3:
    print("please pass two arguments: input edgelist, output dir")
    exit(1)
    
input_file = sys.argv[1]
output_dir = sys.argv[2] 
name = os.path.splitext(os.path.basename(input_file))[0]
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

get_rich_club(input_file, output_dir, name)