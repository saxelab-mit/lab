#!/bin/bash

# purpose: run mark_motion_exclusions.py 

#inputs: (1+, optional) a list of subject IDs in BIDS directories format WITH sub- prefix (e.g. as sub-SAXEEMOfd32)
#       ... if not provided, will run for ALL subjects in BIDS/


#example usage: ./submit_motion_exclusions_array.sh sub-SAXEEMOfd22 sub-SAXEEMOfd31 sub-SAXEEMOfd34 
#   ... or:     ./submit_motion_exclusions_array.sh

# since this script just uses SLURM to call the single_subject.sh file, 
# usage of this script itself does not have be done through SLURM / a job. 
# You can submit from inside an interactive session or from headnode of Openmind. 



proj=`cat ../PATHS.txt`
base=$proj/data/BIDS

subjs=($@)

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

# take the length of the array for indexing 
len=$(expr ${#subjs[@]} - 1) 

echo Spawning ${#subjs[@]} sub-jobs.

# submit the jobs
sbatch --array=0-$len $proj/scripts/4_motion_exclusions/mark_excluded_runs.sh ${subjs[@]}
