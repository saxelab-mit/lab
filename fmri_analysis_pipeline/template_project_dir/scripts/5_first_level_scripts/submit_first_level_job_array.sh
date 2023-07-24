#!/bin/bash

#purpose: run first level script in container 

#inputs: (1) task identifier (e.g.: tomloc ; e.g.: read) ; note: no quotes necessary
# 	 (2) flscript: the name of the python script, e.g. first_level_standard.py (no quotes necessary)
# 	 (3+, optional) a list of subject IDs in BIDS directories format WITH -sub prefix (e.g. as sub-SAXEEMOfd32 )
#       ... if not provided, will run for ALL subjects in BIDS/

#example usage: ./submit_first_level_job_array.sh tomloc first_level_standard.py sub-SAXEEMOfd22 sub-SAXEEMOfd31 sub-SAXEEMOfd34 
#       or..    ./submit_first_level_job_array.sh tomloc first_level_standard.py


# since this script just uses SLURM to call the single_subject.sh file, 
# usage of this script itself does not have be done through SLURM / a job. 
# You can submit from inside an interactive session or from headnode of Openmind. 


proj=`cat ../PATHS.txt`
task=$1
flscript=$2
base=$proj/data/BIDS

subjs=("${@:3}")

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

# submit job 
echo Spawning ${#subjs[@]} sub-jobs.

echo ${subjs[@]}

cmd="sbatch --array=0-$len first_level_single_subject.sh $task $flscript ${subjs[@]}"

echo $cmd
$cmd

