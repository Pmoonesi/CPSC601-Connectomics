import sys
import os
import csv
import networkx as nx
import numpy as np
import pickle

def get_centrality(input_path, output_csv_path, network_name, output_folder):
    try:
        G = nx.read_edgelist(input_path, create_using=nx.DiGraph, data=False)
    except Exception as e:
        print(e)
        return

    n_nodes = G.number_of_nodes()

    # extract lcc 
    if nx.is_weakly_connected(G):
        g_lcc = G
    else:
        largest_cc = max(nx.weakly_connected_components(g), key=len)
        g_lcc = G.subgraph(largest_cc)

    # pagerank
    try:
        pr = nx.pagerank(G)
        pr_vals = list(pr.values())
        pr_min, pr_mean, pr_max = np.min(pr_vals), np.mean(pr_vals), np.max(pr_vals)
    except:
        pr = None
        pr_min, pr_mean, pr_max = -1, -1, -1
        
    # betweenness
    bc = nx.betweenness_centrality(G, k=None) 
    bc_vals = list(bc.values())
    bc_min, bc_mean, bc_max = np.min(bc_vals), np.mean(bc_vals), np.max(bc_vals)

    # eigenvector 
    try:
        ec = nx.eigenvector_centrality(g_lcc, max_iter=1000)
        ec_vals = list(ec.values())
        ec_min, ec_mean, ec_max = np.min(ec_vals), np.mean(ec_vals), np.max(ec_vals)
    except Exception as e:
        print(e)
        ec_min, ec_mean, ec_max = -1, -1, -1

    # closeness 
    cc = nx.closeness_centrality(g_lcc)
    cc_vals = list(cc.values())
    cc_min, cc_mean, cc_max = np.min(cc_vals), np.mean(cc_vals), np.max(cc_vals)

    # save results
    headers = [
        'Network', 'Nodes',
        'PageRank_Min', 'PageRank_Mean', 'PageRank_Max',
        'Betweenness_Min', 'Betweenness_Mean', 'Betweenness_Max',
        'Eigenvector_Min', 'Eigenvector_Mean', 'Eigenvector_Max',
        'Closeness_Min', 'Closeness_Mean', 'Closeness_Max'
    ]
    
    row = [
        network_name, n_nodes,
        pr_min, pr_mean, pr_max,
        bc_min, bc_mean, bc_max,
        ec_min, ec_mean, ec_max,
        cc_min, cc_mean, cc_max
    ]

    file_exists = os.path.isfile(output_csv_path)
    with open(output_csv_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)

    save_dict = {"page": pr, "betweenness": bc, "eigenvector": ec, "closeness": cc}

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(os.path.join(output_folder, network_name + ".pkl"), 'wb') as f:
        pickle.dump(save_dict, f)
    

if len(sys.argv) < 4:
    print("please pass three arguments: input edgelist and output csv path, and centrality output folder")
    exit(1)

input_file = sys.argv[1]
output_csv = sys.argv[2]
output_folder = sys.argv[3]
name = os.path.splitext(os.path.basename(input_file))[0]

get_centrality(input_file, output_csv, name, output_folder)