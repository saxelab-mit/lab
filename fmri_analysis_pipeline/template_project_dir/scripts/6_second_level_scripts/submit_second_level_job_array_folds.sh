#!/bin/bash


#purpose: run second level script for one subject

# since this script just uses SLURM to call the single_subject.sh file, 
# usage of this script itself does not have be done through SLURM / a job. 
# You can submit from inside an interactive session or from headnode of Openmind. 


#inputs: (1) name of first level script (without the ".py")
# 	 (2) task name 
#	 (3) name of second level python script (with extension)
# 	 (4) is using leave one out method? True for yes and False for traditional
# 	 (5+, optional) a list of subject IDs in BIDS directories format WITH sub- prefix (e.g. as sub-SAXEEMOfd32 )
#           If not provided, will run on ALL subjects in BIDS dir
#example usage: 

# 		./submit_second_level_job_array_folds.sh first_level_standard tomloc second_level_folds.py True sub-SAXEEMOfd04 sub-SAXEEMOfd05 
# or..  ./submit_second_level_job_array_folds.sh first_level_standard tomloc second_level_folds.py True 



proj=`cat ../PATHS.txt`
base=$proj/data/BIDS
subjs=("${@:5}")


# if subjs not provided 
if [ ${#subjs[@]} -eq 0 ]; then
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
len=$(expr ${#subjs[@]} - 1) # len - 1

echo Spawning ${#subjs[@]} sub-jobs.
cmd="sbatch --array=0-$len $proj/scripts/6_second_level_scripts/second_level_single_subject.sh $1 $2 $3 $4 ${subjs[@]}"

echo $cmd
$cmd

