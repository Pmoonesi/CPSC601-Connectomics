import snap
import os
import glob
import re
from tqdm import tqdm
from suppress_output import suppress_c_stdout
import networkx as nx

connectome = "adult"
modules_path = f"/home/parham.moonesisohi/connectomics/data/communities/{connectome}_modules/modules/*.edgelist"
base_output_path = f"/home/parham.moonesisohi/connectomics/data/null/null1/{connectome}"
gvoid_path = f"/home/parham.moonesisohi/connectomics/data/communities/{connectome}_modules/void/G_void.edgelist"

number_pattern = re.compile("G_modules_(\d+).edgelist")
module_edgelists = sorted(glob.glob(modules_path))


for i in range(100):
    out_dir = os.path.join(base_output_path, "parts", f"n{i+1}")
    os.makedirs(out_dir, exist_ok=True)

Rnd = snap.TRnd()

# step 1
print("creating the rewired modules")

for module_edgelist in tqdm(module_edgelists):

    # discover the module_n
    module_n = number_pattern.search(module_edgelist).group(1)

    # print(f"module {module_n}:\n\n")

    # read the edgelist
    G_module = snap.LoadEdgeList(snap.TNGraph, module_edgelist, 0, 1)

    for i in tqdm(range(100), leave=False):
        # print(f"making the module {module_n} for null model {i + 1}:")

        with suppress_c_stdout():
            G_module_rewired = snap.GenRewire(G_module, 10, Rnd)

        out_path = os.path.join(base_output_path, "parts", f"n{i+1}", f"G_modules_rewired_{module_n}.edgelist")
        G_module_rewired.SaveEdgeList(out_path)



# step 2
print("creating the full rewired null models (intra perturbed)")

G_void = nx.read_edgelist(gvoid_path, create_using=nx.DiGraph)

for i in tqdm(range(100)):
    rewired_modules_path = sorted(glob.glob(os.path.join(base_output_path, "parts", f"n{i+1}", "*.edgelist")))
    G_modules = [nx.read_edgelist(module_path, create_using=nx.DiGraph) for module_path in rewired_modules_path]
    G_complete = nx.compose(G_void, nx.compose_all(G_modules))

    out_path = os.path.join(base_output_path, f"{connectome}_null1_n{i+1}.edgelist")
    nx.write_edgelist(G_complete, out_path)



