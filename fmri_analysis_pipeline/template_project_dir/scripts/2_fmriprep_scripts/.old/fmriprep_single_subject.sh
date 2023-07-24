#!/bin/bash

#SBATCH -J fmriprep
#SBATCH -t 1-15:00:00
#SBATCH --mem=15GB
#SBATCH --cpus-per-task=8

#purpose: run fmriprep container for one subject

# THIS SCRIPT IS INTENDED TO BE RUN THROUGH THE WRAPPER SCRIPT submit_fmriprep_job_array.sh 
# THE JOB ARRAY WRAPPER SCRIPT TAKES IDENTICAL ARGUMENTS AND CAN ALSO BE USED FOR SINGLE SUBJECT

#inputs: (1+) a list of subject IDs in BIDS directories format (WITH 'sub-' prefix, no underscores such as: sub-SAXEEMOfd32, when the original subject ID was SAXE_EMOfd_32)

#example usage: sbatch fmriprep_single_subject.sh sub-SAXEEMOfd22 sub-SAXEEMOfd31 sub-SAXEEMOfd34 


proj=`cat ../PATHS.txt`
bids_dir=$proj/data/BIDS
out_dir=$bids_dir/derivatives/

subjs=("${@:1}")

scratch=$proj/working_dir
if [ ! -d $scratch ]; then
  mkdir -p $scratch
fi

module add openmind/singularity
module add openmind/freesurfer/6.0.0


subject=$(echo ${subjs[${SLURM_ARRAY_TASK_ID}]}) 

templateflow=/om3/group/saxelab/LAB_STANDARD_fMRI_CODE/singularity_images_master/TEMPLATEFLOW
export TEMPLATEFLOW_HOME=$templateflow
export SINGULARITYENV_TEMPLATEFLOW_HOME=$templateflow

echo "Submitted job for: ${subject}"

# run fmriprep for current subject 
cmd="singularity exec --cleanenv -B /om:/om -B /om3:/om3 -B /cm:/cm -B /om2:/om2 -B /nese:/nese $proj/singularity_images/fmriprep_templateflow.sif fmriprep $bids_dir $out_dir participant --participant_label $subject --mem_mb 15000 --ignore slicetiming --use-aroma -w $scratch --fs-license-file /cm/shared/openmind/freesurfer/6.0.0/.license --output-spaces MNI152NLin6Asym:res-2"

# execute command
$cmd 