#!/bin/bash

# usage: ./submit_heudiconv_array.sh heudi.py

heudifile=$1

proj_dir=`cat ../../PATHS.txt`

# first go to data directory, grab all subjects,
# and assign to an array
pushd $proj_dir/data/BIDS

#TODO: Fix this -- read from subjectlist.txt file
subjs=($(ls sub-* -d -1))

popd

# take the length of the array
# this will be useful for indexing later
len=$(expr ${#subjs[@]} - 1) # len - 1

echo Spawning ${#subjs[@]} sub-jobs.

sbatch --array=0-$len $proj_dir/scripts/12_anonymize_scripts/anon_heudiconv_single_subject.sh $heudifile ${subjs[@]}
