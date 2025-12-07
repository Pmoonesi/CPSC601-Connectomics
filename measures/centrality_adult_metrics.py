import sys
import os
import csv
import random
import snap
import pickle

FRAC = 0.005
SAMPLES = 1000

def save_dict(data_dict, output_dir, network_name, suffix):
    filename = f"{network_name}_{suffix}.pkl"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as f:
        pickle.dump(data_dict, f)

def get_approx_closeness(graph, samples=1000):
    n = graph.GetNodes()
    if n < 2: return 0.0, 0.0, 0.0, {}

    # select random nodes
    node_vec = snap.TIntV()
    for ni in graph.Nodes():
        node_vec.Add(ni.GetId())

    total_nodes = node_vec.Len()
    all_ids = [node_vec[i] for i in range(total_nodes)]

    if samples >= total_nodes:
        targets = all_ids
    else:
        targets = random.sample(all_ids, samples)


    # calculate closeness for sampled nodes
    closeness_dict = {}
    for nid in targets:
        val = snap.GetClosenessCentr(graph, nid, True, True)
        closeness_dict[nid] = val

    vals = list(closeness_dict.values())
    if not vals: return 0.0, 0.0, 0.0, {}

    return min(vals), sum(vals)/len(vals), max(vals), closeness_dict

def get_centrality(input_path, output_csv_path, network_name):
    base_dir = os.path.dirname(output_csv_path)
    pickle_dir = os.path.join(base_dir, "centrality_ad")
    os.makedirs(pickle_dir, exist_ok=True)

    try:
        G = snap.LoadEdgeList(snap.TNGraph, input_path, 0, 1)
    except Exception as e:
        print(e)
        return

    n_nodes = G.GetNodes()

    # extract lcc
    mx_wcc = snap.GetMxWcc(G)
    lcc_nodes = mx_wcc.GetNodes()
    mx_wcc_und = mx_wcc.ConvertGraph(snap.TUNGraph)

    # pagerank
    pr_rank_h = snap.TIntFltH()
    snap.GetPageRank(G, pr_rank_h, 0.85, 1e-4, 100)

    pr_dict = {}
    pr_sum, pr_max, pr_min = 0.0, -1.0, 1.0

    for ni in G.Nodes():
        nid = ni.GetId()
        val = pr_rank_h[nid]
        pr_dict[nid] = val
        pr_sum += val
        if val > pr_max: pr_max = val
        if val < pr_min: pr_min = val

    pr_mean = pr_sum / n_nodes

    # betweenness 
    nodes_h = snap.TIntFltH()
    edges_h = snap.TIntPrFltH()
    snap.GetBetweennessCentr(G, nodes_h, edges_h, FRAC)

    bc_dict = {}
    bc_sum, bc_max, bc_min = 0.0, -1.0, float('inf')

    for nid in nodes_h:
        val = nodes_h[nid]
        bc_dict[nid] = val
        bc_sum += val
        if val > bc_max: bc_max = val
        if val < bc_min: bc_min = val

    bc_mean = bc_sum / n_nodes
    if bc_min == float('inf'): bc_min = 0.0

    # eigenvector
    nid_eigen_h = snap.TIntFltH()
    snap.GetEigenVectorCentr(mx_wcc_und, nid_eigen_h, 1e-4, 100) ## uses undirected only

    ev_dict = {}
    ev_sum, ev_max, ev_min = 0.0, -1.0, float('inf')

    for nid in nid_eigen_h:
        val = nid_eigen_h[nid]
        ev_dict[nid] = val
        ev_dict[nid] = val
        ev_sum += val
        if val > ev_max: ev_max = val
        if val < ev_min: ev_min = val

    ev_mean = ev_sum / lcc_nodes if lcc_nodes > 0 else 0
    if ev_min == float('inf'): ev_min = 0.0

    # closeness (lcc only, estimated)
    cc_min, cc_mean, cc_max, cc_dict = get_approx_closeness(mx_wcc, samples=SAMPLES)

    # save results
    headers = [
        'Network', 'Nodes', 'LCC_Nodes',
        'PageRank_Mean', 'PageRank_Max', 'PageRank_Min',
        'Betweenness_Mean', 'Betweenness_Max', 'Betweenness_Min',
        'Eigenvector_Mean', 'Eigenvector_Max', 'Eigenvector_Min',
        'Closeness_Mean', 'Closeness_Max', 'Closeness_Min'
    ]

    row = [
        network_name, n_nodes, lcc_nodes,
        pr_mean, pr_max, pr_min,
        bc_mean, bc_max, bc_min,
        ev_mean, ev_max, ev_min,
        cc_mean, cc_max, cc_min
    ]

    file_exists = os.path.isfile(output_csv_path)
    with open(output_csv_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)

    to_save = {"page": pr_dict, "betweenness": bc_dict, "eigenvector": ev_dict, "closeness": cc_dict}
    save_dict(to_save, pickle_dir, network_name, "centralities")


# main execution
if len(sys.argv) < 3:
    print("please pass two arguments, the input edgelist and the output csv path")
    exit(1)

input_file = sys.argv[1]
output_csv = sys.argv[2]
name = os.path.splitext(os.path.basename(input_file))[0]

get_centrality(input_file, output_csv, name)