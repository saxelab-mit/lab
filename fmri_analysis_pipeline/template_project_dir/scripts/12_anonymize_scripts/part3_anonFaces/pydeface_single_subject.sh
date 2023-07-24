#!/bin/bash -l

#SBATCH -J pydeface
#SBATCH -t 2:00:00
#SBATCH --mem=10GB
#SBATCH --cpus-per-task=1

bidsanon=$1
args=($@)
subjs=(${args[@]:1}) # drop initial args

subject=${subjs[${SLURM_ARRAY_TASK_ID}]}

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

echo "Submitted job for: ${subject}"

singularity exec -B /cm:/cm -B /nese:/nese -B /om:/om -B /om2:/om2 -B /om3:/om3 $bidsanon/../../singularity_images/pydeface.sif /neurodocker/startup.sh $bidsanon/../../scripts/12_anonymize_scripts/part3_anonFaces/pydeface.sh $bidsanon $subject


