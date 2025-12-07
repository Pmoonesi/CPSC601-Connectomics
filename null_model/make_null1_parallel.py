import snap
import random
import os
import glob
import re
from tqdm import tqdm
from suppress_output import suppress_c_stdout
import networkx as nx
from concurrent.futures import ProcessPoolExecutor

connectome = "larvae"
modules_path = f"/home/parham.moonesisohi/connectomics/data/communities/{connectome}_modules/modules/*.edgelist"
base_output_path = f"/home/parham.moonesisohi/connectomics/data/null/null1/{connectome}"
gvoid_path = f"/home/parham.moonesisohi/connectomics/data/communities/{connectome}_modules/void/G_void.edgelist"

number_pattern = re.compile("G_modules_(\d+).edgelist")
module_edgelists = sorted(glob.glob(modules_path))


for i in range(100):
    out_dir = os.path.join(base_output_path, "parts", f"n{i+1}")
    os.makedirs(out_dir, exist_ok=True)

def step1_task(args):
    """
        args: (module_path, output_filepath, unique_seed)
    """
    module_path, output_filepath, unique_seed = args

    G_module = snap.LoadEdgeList(snap.TNGraph, module_path, 0, 1)

    Rnd = snap.TRnd(unique_seed, 0) # seed, burn-in

    with suppress_c_stdout():
        G_module_rewired = snap.GenRewire(G_module, 10, Rnd)

    G_module_rewired.SaveEdgeList(output_filepath)

    return True

# step 1
print("creating the rewired modules")

with ProcessPoolExecutor() as executor:
        
    # Outer Loop: Iterate modules sequentially
    for module_edgelist in tqdm(module_edgelists):
        module_n = number_pattern.search(module_edgelist).group(1)
            
        # Prepare 100 tasks for this module
        tasks = []
        for i in range(100):
                
            out_path = os.path.join(base_output_path, "parts", f"n{i+1}", f"G_modules_rewired_{module_n}.edgelist")
                
            unique_seed = random.randint(0, 2_000_000_000)
                
            tasks.append((module_edgelist, out_path, unique_seed))
            
        results = list(executor.map(step1_task, tasks))

        if sum(results) != 100:
            tqdm.write(f"module {module_n} did not finish all rewiring successfully!")

def step2_task(args):
    """
        args: ()
    """
    rewired_modules_pattern, void_path, output_path = args
    
    rewired_modules_path = sorted(glob.glob(rewired_modules_pattern))

    G_modules = [nx.read_edgelist(module_path, create_using=nx.DiGraph) for module_path in rewired_modules_path]
    G_void = nx.read_edgelist(void_path, create_using=nx.DiGraph)
    G_complete = nx.compose(G_void, nx.compose_all(G_modules))

    nx.write_edgelist(G_complete, output_path)
    return True


# step 2
#print("creating the full rewired null models (intra perturbed)")

#with ProcessPoolExecutor() as executor:

    #tasks = []

    #for i in range(100):
        #rewired_modules_pattern = os.path.join(base_output_path, "parts", f"n{i+1}", "*.edgelist")
        #out_path = os.path.join(base_output_path, f"{connectome}_null1_n{i+1}.edgelist")
        #tasks.append((rewired_modules_pattern, gvoid_path, out_path))

    #results = list(executor.map(step2_task, tasks))

    #if sum(results) != 100:
        #tqdm.write(f"step 2 did not complete successfully!")

#G_void = nx.read_edgelist(gvoid_path, create_using=nx.DiGraph)

#for i in tqdm(range(100)):
#    rewired_modules_path = sorted(glob.glob(os.path.join(base_output_path, "parts", f"n{i+1}", "*.edgelist")))[:20]
#    G_modules = [nx.read_edgelist(module_path, create_using=nx.DiGraph) for module_path in rewired_modules_path]
#    G_complete = nx.compose(G_void, nx.compose_all(G_modules))
#    break
#    out_path = os.path.join(base_output_path, f"{connectome}_null1_n{i+1}.edgelist")
#    nx.write_edgelist(G_complete, out_path)



