import sys
import os
import csv
import numpy as np
import networkx as nx
import bct

def get_rich_club(input_path, output_dir, network_name):
    try:
        G = nx.read_edgelist(input_path, create_using=nx.DiGraph, data=False)
    except Exception as e:
        print(e)
        return

    adj_matrix = nx.to_numpy_array(G)
    adj_matrix = (adj_matrix > 0).astype(float)

    # rich club (binary directed) (coef, nodes left, edges left)
    phi, nk, ek = bct.rich_club_bd(adj_matrix)
    
    curve_filename = f"{network_name}_rich_club_curve.csv"
    curve_path = os.path.join(output_dir, curve_filename)
    
    with open(curve_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['k', 'phi', 'n_club', 'e_club'])
        
        for i in range(len(phi)):
            k = i + 1
            val_phi = phi[i]
            val_n = int(nk[i])
            val_e = int(ek[i])
            
            if np.isnan(val_phi):
                if val_n < 2: continue
                val_phi = 0.0
            
            writer.writerow([k, val_phi, val_n, val_e])
            

if len(sys.argv) < 3:
    print("please pass two arguments: input edgelist and output dir")
    exit(1)
    
input_file = sys.argv[1]
output_dir = sys.argv[2]
name = os.path.splitext(os.path.basename(input_file))[0]

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

get_rich_club(input_file, output_dir, name)