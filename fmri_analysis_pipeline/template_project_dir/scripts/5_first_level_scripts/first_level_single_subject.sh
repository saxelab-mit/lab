#!/bin/bash -l

#SBATCH -J first_level
#SBATCH -t 4:00:00
#SBATCH --mem=25GB
#SBATCH --cpus-per-task=4

#purpose: run first level script in container for one subject

# THIS SCRIPT IS INTENDED TO BE RUN THROUGH THE WRAPPER SCRIPT submit_first_level_job_array.sh 
# THE JOB ARRAY WRAPPER SCRIPT CAN ALSO BE USED FOR SINGLE SUBJECT


proj=`cat ../PATHS.txt`
task=$1
flscript=$2
fmriprep_dir=$proj/data/BIDS/derivatives/fmriprep

subjs=("${@:3}")

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

subject=$(echo ${subjs[${SLURM_ARRAY_TASK_ID}]})


# get the flscript as non- .py name to use in dir creations
l=$((${#flscript} - 3))
flscript_noExt=$(echo "${flscript:0:$l}")

echo "Submitted job for: ${subject} ${task} ${flscript}"
echo "SUBJECT IS: ______________"
echo $subject 


# FIRST CONCATENATE BRAIN MASKS
cmd="singularity exec -B /om3:/om3 -B /om:/om -B /cm:/cm -B /om2:/om2 -B /nese:/nese $proj/singularity_images/univariate_general.sif /neurodocker/startup.sh \
python $proj/scripts/5_first_level_scripts/concat_brain_masks.py -f $fmriprep_dir -s $subject"
## add optional session ID eg after '-f $fmriprep_dir' include '-ss ses-1'

echo $cmd
$cmd 

cmd2="singularity exec -B /om3:/om3 -B /om:/om -B /cm:/cm -B /om2:/om2 -B /nese:/nese $proj/singularity_images/nipype_env.simg /neurodocker/startup.sh \
python $proj/scripts/5_first_level_scripts/$flscript $proj/data/BIDS \
-f $proj/data/BIDS/derivatives/fmriprep \
-w $proj/working_dir/$flscript_noExt \
-o $proj/Analysis/$flscript_noExt \
-t $task -s $subject"

echo $cmd2
$cmd2


