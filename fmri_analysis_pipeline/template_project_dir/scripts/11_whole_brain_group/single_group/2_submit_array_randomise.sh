#!/bin/bash

# CONTRAST MUST BE SET TO THE ALREADY EXISTING FOLDER OUTPUT BY randomize_group_level.ipynb 
# THIS IS BASED ON THE NAME PROVIDED IN contrasts VARIABLE OF THE NOTEBOOK 

# example: 
# ./submit_randomise_step2_array.sh 

# this submits an array of jobs (each by calling the single_contrast batch script) to run the randomise command for a single group


proj=`cat ../../PATHS.txt`
group_analysis_dir="$proj/TIER/analysis_data/group_analysis"

directories=( $(find $group_analysis_dir/ -type d -name "randomise_*") )
len=$(expr ${#directories[@]} - 1) 

cmd="sbatch --array=0-$len randomise_step2_single_contrast.sh ${directories[@]}"

echo $cmd
echo $len
$cmd

