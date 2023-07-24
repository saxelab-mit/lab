#!/bin/bash

#purpose: run fmriprep container 

#inputs: (1+, optional) a list of subject IDs in BIDS directories format (WITH 'sub-' prefix, no underscores such as: sub-SAXEEMOfd32)
#           ... if not provided, will run for ALL subjects in BIDS 

#example usage: ./submit_fmriprep_job_array.sh sub-SAXEEMOfd22 sub-SAXEEMOfd31 
#		or..    ./submit_fmriprep_job_array.sh  


# since this script just uses SLURM to call the single_subject.sh file, 
# usage of this script itself does not have be done through SLURM / a job. 
# You can submit from inside an interactive session or from headnode of Openmind. 


subjs=($@)

proj=`cat ../PATHS.txt`
base=$proj/data/BIDS

if [[ $# -eq 0 ]]; then
    # first go to data directory, grab all subjects,
    # and assign to an array
    pushd $base
    # including pilots
    subjs=($(ls sub-* -d))
    # excluding pilots
    #subjs=($(ls sub-leap[0-9]* -d))
    popd
fi


# take the length of the array
# this will be useful for indexing later
len=$(expr ${#subjs[@]} - 1) # len - 1

echo Spawning ${#subjs[@]} sub-jobs.

sbatch --array=0-$len%25 $proj/scripts/2_fmriprep_scripts/fmriprep_single_subject.sh $base ${subjs[@]}
