#!/bin/bash -l

#SBATCH -J second_level
#SBATCH -t 1:00:00
#SBATCH --mem=15GB
#SBATCH --cpus-per-task=4
#SBATCH -p saxelab

#purpose: run second level script for one subject

# THIS SCRIPT IS INTENDED TO BE RUN THROUGH THE WRAPPER SCRIPT submit_second_level_job_array_folds.sh 
# THE JOB ARRAY WRAPPER SCRIPT CAN ALSO BE USED FOR SINGLE SUBJECT


proj=`cat ../PATHS.txt`
first_level_analysis_dir=$proj/Analysis/$1
task=$2
slscript=$3
isUsingLeaveOneOut=$4

subjs=("${@:5}")

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7


subject=$(echo ${subjs[${SLURM_ARRAY_TASK_ID}]}) 

l=$((${#slscript} - 3))
slscript_noExt=$(echo "${slscript:0:$l}")

echo "Submitted job for: ${subject}"

cmd="singularity exec -B /om:/om -B /om3:/om3 -B /nese:/nese -B /om2:/om2 -B /cm:/cm $proj/singularity_images/nipype_env.simg /neurodocker/startup.sh \
python $proj/scripts/6_second_level_scripts/$slscript $proj/data/BIDS \
$first_level_analysis_dir \
-w $proj/working_dir/$slscript_noExt \
-o $proj/Analysis/$slscript_noExt \
-t $task -s $subject -l $isUsingLeaveOneOut"

echo $cmd

$cmd


