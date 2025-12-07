import sys
import os
import csv
import numpy as np
import networkx as nx
import bct

def get_metrics(input_path, output_csv_path, network_name):
    try:
        G = nx.read_edgelist(input_path, create_using=nx.DiGraph, data=False)
    except Exception as e:
        print(e)
        return

    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()

    adj_matrix = nx.to_numpy_array(G)
    adj_matrix = (adj_matrix > 0).astype(float)

    # clustering coefficient
    clust_vector = bct.clustering_coef_bd(adj_matrix)
    avg_clustering = np.mean(clust_vector)

    # global efficiency
    global_eff = bct.efficiency_bin(adj_matrix)

    # local efficiency
    local_eff_vector = bct.efficiency_bin(adj_matrix, local=True)
    avg_local_eff = np.mean(local_eff_vector)

    # # characteristic path length
    # distance_matrix = bct.distance_bin(adj_matrix)
    # char_path_len, _, _, _, _ = bct.charpath(distance_matrix)

    # save results
    file_exists = os.path.isfile(output_csv_path)
    
    with open(output_csv_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['network', 'nodes', 'edges', 'clustering', 'global_eff', 'local_eff'])
        
        writer.writerow([network_name, n_nodes, n_edges, avg_clustering, global_eff, avg_local_eff])
    

if len(sys.argv) < 3:
    print("please pass two arguments, the input edgelist and the output csv path")
    exit(1)

input_file = sys.argv[1]
output_csv = sys.argv[2]
name = os.path.basename(input_file).replace(".csv", "")

get_metrics(input_file, output_csv, name)