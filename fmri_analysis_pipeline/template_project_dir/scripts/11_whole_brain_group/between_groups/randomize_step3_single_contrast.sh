#!/bin/bash -l

#SBATCH -t 3:00:00
#SBATCH -n 1
#SBATCH -c 24
#SBATCH --mem=5G


directories=($@)
dir=${directories[${SLURM_ARRAY_TASK_ID}]}

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7
module load openmind/fsl/5.0.9

echo Submitted job for: ${dir}

cd $dir
randomise -i all_copes.nii.gz -o TwoSampT -d design.mat -t design.con -m avg152T1_brain.nii.gz -x


