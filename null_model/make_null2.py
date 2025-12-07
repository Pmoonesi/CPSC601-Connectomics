import snap
import os
import glob
import re
from tqdm import tqdm
from suppress_output import suppress_c_stdout
import networkx as nx

connectome = "adult"
modules_path = f"/home/parham.moonesisohi/connectomics/data/communities/{connectome}_modules/modules/*.edgelist"
base_output_path = f"/home/parham.moonesisohi/connectomics/data/null/null2/{connectome}"
gvoid_path = f"/home/parham.moonesisohi/connectomics/data/communities/{connectome}_modules/void/G_void.edgelist"

number_pattern = re.compile("G_modules_(\d+).edgelist")
module_edgelists = sorted(glob.glob(modules_path))

for i in range(100):
    out_dir = os.path.join(base_output_path, "parts", f"n{i+1}")
    os.makedirs(out_dir, exist_ok=True)

Rnd = snap.TRnd()

# step 1
print("creating the rewired voids")

#G_void = nx.read_edgelist(gvoid_path, create_using=nx.DiGraph)
G_void = snap.LoadEdgeList(snap.TNGraph, gvoid_path, 0, 1)

for i in tqdm(range(100)):
    
    with suppress_c_stdout():
        G_void_rewired = snap.GenRewire(G_void, 10, Rnd)
    
    out_path = os.path.join(base_output_path, "parts", f"n{i+1}", f"G_void_rewired.edgelist")

    G_void_rewired.SaveEdgeList(out_path)


G_modules = nx.DiGraph()
for module_edgelist in tqdm(module_edgelists):

    # read the edgelist
    G_module = nx.read_edgelist(module_edgelist, create_using=nx.DiGraph)
    
    G_modules = nx.compose(G_modules, G_module)
    

# step 2
print("creating the full rewired null models (intra perturbed)")

for i in tqdm(range(100)):

    G_void_rewired_path = os.path.join(base_output_path, "parts", f"n{i+1}", f"G_void_rewired.edgelist")
    G_void_rewired = nx.read_edgelist(G_void_rewired_path, create_using=nx.DiGraph)
    G_complete = nx.compose(G_void_rewired, G_modules)

    out_path = os.path.join(base_output_path, f"{connectome}_null2_n{i+1}.edgelist")
    nx.write_edgelist(G_complete, out_path)



