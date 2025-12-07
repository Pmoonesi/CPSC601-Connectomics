#!/bin/bash
#SBATCH --job-name=null2_adult
#SBATCH --time=01-00:00:00        
#SBATCH --mem=64G               
#SBATCH --ntasks=1
#SBATCH --partition=cpu2023,cpu2022,cpu2022-bf24,cpu2021
#SBATCH --cpus-per-task=16      
#SBATCH --output=logs/null2_%a.out  

source ~/software/init-python
source ~/envs/snap-py37/bin/activate

mkdir -p logs

python make_null2.py 
