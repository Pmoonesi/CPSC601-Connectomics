#!/bin/bash
#SBATCH --job-name=merge_nulls
#SBATCH --time=01:00:00        
#SBATCH --mem=8G               
#SBATCH --ntasks=1
#SBATCH --partition=cpu2023,cpu2022,cpu2022-bf24,cpu2021
#SBATCH --cpus-per-task=8      
#SBATCH --array=0-99%32          
#SBATCH --output=logs/merge_%a.out  

source ~/software/init-python
source ~/envs/snap-py37/bin/activate

mkdir -p logs

echo "Starting task $SLURM_ARRAY_TASK_ID"
python merge_task.py $SLURM_ARRAY_TASK_ID
