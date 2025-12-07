import snap
import os


#original_path = "/home/parham.moonesisohi/connectomics/data/adult/connections_ws.csv"
original_path = "/home/parham.moonesisohi/connectomics/data/larvae/larvae_ws.csv"
#output_directory = "/home/parham.moonesisohi/connectomics/data/null/adult"
output_directory = "/home/parham.moonesisohi/connectomics/data/null/larvae"

G_orig = snap.LoadEdgeList(snap.TNGraph, original_path, 0, 1)

Rnd = snap.TRnd()
for i in range(100):
    print(f"making the null model {i+1}:")
    G_rewired = snap.GenRewire(G_orig, 10, Rnd)
    outpath = os.path.join(output_directory, f"larvae_null0_n{i+1}.txt")
    G_rewired.SaveEdgeList(outpath)

