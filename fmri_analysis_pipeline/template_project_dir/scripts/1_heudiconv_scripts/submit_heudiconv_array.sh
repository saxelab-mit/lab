#!/bin/bash

#purpose: run heudiconv  

# THIS SCRIPT IS INTENDED TO BE RUN THROUGH THE WRAPPER SCRIPT submit_heudiconv_array.sh 
# THE JOB ARRAY WRAPPER SCRIPT TAKES IDENTICAL ARGUMENTS AND CAN ALSO BE USED FOR SINGLE SUBJECT

#inputs:
# 	 (1+) a list of subject IDs in their original format from dicoms/ directory (e.g. SAXE_EMOfd_20 )
#         if not provided, will run for ALL subjects in dicoms/

#example usage: ./submit_heudiconv_array.sh SAXE_EMOfd_20 SAXE_EMOfd_32 
# 	    or...   ./submit_heudiconv_array.sh 


# note: assumes heuristics file is in this dir within: heuristic_files/heudi.py 
heudifile=heuristic_files/heudi.py

proj=`cat ../PATHS.txt`

subjs=("${@}")

if [[ $# -eq 0 ]]; then
    # first go to data directory, grab all subjects,
    # and assign to an array
    pushd $proj/data/dicoms
    # including pilots
    subjs=($(ls SAX* -d))
    # excluding pilots
    #subjs=($(ls sub-leap[0-9]* -d))
    popd
fi


# take the length of the array for indexing job
len=$(expr ${#subjs[@]} - 1) 

echo Spawning ${#subjs[@]} sub-jobs.

# submit the jobs
sbatch --array=0-$len $proj/scripts/1_heudiconv_scripts/heudiconv_single_subject.sh $heudifile ${subjs[@]}
