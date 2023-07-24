#!/bin/bash

# CONTRAST MUST BE SET TO THE ALREADY EXISTING FOLDER OUTPUT BY randomize_group_level.ipynb 
# THIS IS BASED ON THE NAME PROVIDED IN contrasts VARIABLE OF THE NOTEBOOK 

contrast_fname='group_analysis_output_endorse_gt_oppose_randomise'
# contrast='group_analysis_output_oppose_gt_endorse_randomise'

proj=`cat ../../../PATHS.txt`
randomise_dir="$proj/TIER/analysis_data/group_flame/$contrast_fname"

directories=( $(find $randomise_dir/ -type d -name "randomise_read_con_*") )
len=$(expr ${#directories[@]} - 1) 

cmd="sbatch --array=0-$len randomize_step3_single_contrast.sh ${directories[@]}"

echo $cmd
echo $len
$cmd

