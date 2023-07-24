#!/bin/bash
# usage:
# bash anonymize_part3_pydeface.sh 

proj_dir=`cat ../../PATHS.txt`
bidsanon=$proj_dir/data/BIDS_anon

pushd $bidsanon

subjs=($(ls sub-* -d -1))

popd

len=$(expr ${#subjs[@]} - 1) # len - 1

echo Spawning ${#subjs[@]} sub-jobs.

sbatch --array=0-$len $proj_dir/scripts/12_anonymize_scripts/part3_anonFaces/pydeface_single_subject.sh $bidsanon ${subjs[@]}

