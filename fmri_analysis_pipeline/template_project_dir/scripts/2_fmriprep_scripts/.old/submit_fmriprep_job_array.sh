#!/bin/bash

#purpose: run fmriprep container 

#inputs: (1+) a list of subject IDs in BIDS directories format (WITH 'sub-' prefix, no underscores such as: sub-SAXEEMOfd32, when the original subject ID was SAXE_EMOfd_32)

#example usage: ./submit_fmriprep_job_array.sh sub-SAXEEMOfd22 sub-SAXEEMOfd31 
#		./submit_fmriprep_job_array.sh sub-SAXEEMOfd22 


# since this script just uses SLURM to call the single_subject.sh file, 
# usage of this script itself does not have be done through SLURM / a job. 
# You can submit from inside an interactive session or from headnode of Openmind. 



proj=`cat ../PATHS.txt`

subjs=("${@:1}")



# take the length of the array for indexing job
len=$(expr ${#subjs[@]} - 1) 

echo Spawning ${#subjs[@]} sub-jobs.

# submit the jobs 
sbatch --array=0-$len $proj/scripts/2_fmriprep_scripts/fmriprep_single_subject.sh ${subjs[@]}
