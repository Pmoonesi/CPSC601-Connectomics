import sys
import os
import csv
import random
import snap
import time

GLOBAL_EFF_SAMPLES = 1000

def _get_subgraph_global_efficiency(Graph, is_directed=True):
    N = Graph.GetNodes()
    if N < 2: return 0.0
    
    sum_inv_dist = 0.0
    
    # bfs for path lengths
    for NI in Graph.Nodes():
        src_id = NI.GetId()
        NIdToDistH = snap.TIntH()
        snap.GetShortPath(Graph, src_id, NIdToDistH, is_directed)
        
        for dest_id in NIdToDistH:
            dist = NIdToDistH[dest_id]
            if src_id != dest_id and dist > 0:
                sum_inv_dist += (1.0 / dist)
    
    normalization = N * (N - 1)
    return sum_inv_dist / normalization

def _calculate_node_local_efficiency(Graph, Node, is_directed):
    # collect in/out neighbors
    NeighborIds = snap.TIntV()
    for i in range(Node.GetOutDeg()):
        NeighborIds.Add(Node.GetOutNId(i))
        
    if is_directed:
        for i in range(Node.GetInDeg()):
            NeighborIds.Add(Node.GetInNId(i))
            
    if NeighborIds.Len() < 2:
        return 0.0
        
    # induced subgraph
    try:
        SubG = snap.GetSubGraph(Graph, NeighborIds)
    except:
        return 0.0
    
    return _get_subgraph_global_efficiency(SubG, is_directed)

def get_global_efficiency_approx(Graph, sample_size=1000, is_directed=True):
    N = Graph.GetNodes()
    if N < 2: return 0.0
    
    # sample source nodes
    all_node_ids = [NI.GetId() for NI in Graph.Nodes()]
    if sample_size >= N:
        targets = all_node_ids
        actual_sample_size = N
    else:
        targets = random.sample(all_node_ids, sample_size)
        actual_sample_size = sample_size
        
    sum_inv_dist = 0.0
    
    for src_id in targets:
        NIdToDistH = snap.TIntH()
        snap.GetShortPath(Graph, src_id, NIdToDistH, is_directed)
        
        for dest_id in NIdToDistH:
            dist = NIdToDistH[dest_id]
            if src_id != dest_id and dist > 0:
                sum_inv_dist += (1.0 / dist)
                
    normalization = float(actual_sample_size) * float(N - 1)
    return sum_inv_dist / normalization

def get_local_efficiency_exact(Graph, is_directed=True):
    N = Graph.GetNodes()
    if N < 2: return 0.0

    sum_local_eff = 0.0
    
    for NI in Graph.Nodes():
        loc_eff = _calculate_node_local_efficiency(Graph, NI, is_directed)
        sum_local_eff += loc_eff
            
    return sum_local_eff / N

def get_metrics(input_path, output_csv_path, network_name):
    try:
        G = snap.LoadEdgeList(snap.TNGraph, input_path, 0, 1)
    except Exception as e:
        print(e)
        return

    n_nodes = G.GetNodes()
    n_edges = G.GetEdges()

    clustering_coeff = snap.GetClustCf(G, -1)
    global_eff = get_global_efficiency_approx(G, sample_size=GLOBAL_EFF_SAMPLES, is_directed=True)
    local_eff = get_local_efficiency_exact(G, is_directed=True)

    # append to csv
    file_exists = os.path.isfile(output_csv_path)
    with open(output_csv_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['network', 'nodes', 'edges', 'clustering', 'global_eff', 'local_eff'])
        
        writer.writerow([network_name, n_nodes, n_edges, clustering_coeff, global_eff, local_eff])
    
if len(sys.argv) < 3:
    print("please pass two arguments, the input edgelist and the output csv path")
    exit(1)
    
input_file = sys.argv[1]
output_csv = sys.argv[2]
name = os.path.basename(input_file).replace(".edgelist", "").replace(".txt", "").replace(".csv", "")

get_metrics(input_file, output_csv, name)