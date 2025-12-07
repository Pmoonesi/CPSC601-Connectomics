import os
import glob
import numpy as np
import networkx as nx
import snap
import sys

def get_larvae_degrees(input_dir, output_file):
    files = sorted(glob.glob(os.path.join(input_dir, "*ws.csv")))
    
    if not files:
        print("no files found")
        return

    matrix = []
    
    for i, f in enumerate(files):
        try:
            # read as directed, ignore weights
            g = nx.read_edgelist(f, create_using=nx.DiGraph, data=False)
            
            # just append degrees in the order they appear
            degrees = [deg for _, deg in g.degree()]
            matrix.append(degrees)
                
        except Exception as e:
            print(e)

    try:
        np_matrix = np.array(matrix)
        np.save(output_file, np_matrix)
    except Exception as e:
        print(e)

def get_adult_degrees(input_dir, output_file):
    files = sorted(glob.glob(os.path.join(input_dir, "*adult_ws.csv")))
    
    if not files:
        print("no files found")
        return

    matrix = []
    
    for i, f in enumerate(files):
        try:
            g = snap.LoadEdgeList(snap.TNGraph, f, 0, 1)
            
            deg_list = []
            for ni in g.Nodes():
                deg_list.append(ni.GetDeg())
            
            matrix.append(deg_list)
            
        except Exception as e:
            print(e)
            
    try:
        np_matrix = np.array(matrix)
        np.save(output_file, np_matrix)
    except Exception as e:
        print(e)

# main execution
if len(sys.argv) < 4:
    print("pass three arguments: the connectome, the input directory and the output directory")
    exit(1)
    
conn = sys.argv[1].lower()
in_dir = sys.argv[2]
out_file = sys.argv[3]

if conn == "larvae":
    get_larvae_degrees(in_dir, out_file)
elif conn == "adult":
    get_adult_degrees(in_dir, out_file)
else:
    print("invalid connectome")