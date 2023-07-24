#!/bin/bash -l

#SBATCH -t 3:00:00
#SBATCH -n 1
#SBATCH -c 24
#SBATCH --mem=5G

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7
module load openmind/fsl/5.0.9

directories=($@)
dir=${directories[${SLURM_ARRAY_TASK_ID}]}

echo Submitted job for: ${dir}

cd $dir
randomise -i all_copes.nii.gz -o randomise_onesampT -1 -v 6 -T 




