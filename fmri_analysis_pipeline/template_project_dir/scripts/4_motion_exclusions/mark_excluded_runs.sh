#!/bin/bash -l

#SBATCH -J excl_motion
#SBATCH -t 2:00:00
#SBATCH --mem=8GB


# purpose: run mark_motion_exclusions.py for a single subject 

# THIS SCRIPT IS INTENDED TO BE RUN THROUGH THE WRAPPER SCRIPT submit_motion_exclusions_array.sh 
# THE JOB ARRAY WRAPPER SCRIPT CAN ALSO BE USED FOR SINGLE SUBJECT


proj=`cat ../PATHS.txt`

subjs=("${@:1}")


subject=$(echo ${subjs[${SLURM_ARRAY_TASK_ID}]}) 

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7


echo "RUNNING FOR SUBJECT:"
echo $subject
echo "____________________"

singularity exec --cleanenv -B /om:/om -B /om2:/om2 -B /cm:/cm -B /om3:/om3 -B /nese:/nese $proj/singularity_images/nipype_env.simg \
/neurodocker/startup.sh python $proj/scripts/4_motion_exclusions/mark_motion_exclusions.py $proj $subject
