#!/bin/bash
# usage
    # bash anonymize_part1_createBIDSanon.sh true 
    # bash anonymize_part1_createBIDSanon.sh false


convert=$1 # True if you want to anonymize participant IDs, false if you just want to copy over the BIDS directory

study_root=`cat ../../PATHS.txt`

if [ "$convert" = true ]; then
    heudifile=$study_root/scripts/1_heudiconv_scripts/heuristic_files/heudi.py
    bash submit_anon_heudiconv_array.sh $heudifile
else
    rsync -av --progress $study_root/data/BIDS/ $study_root/data/BIDS_anon --exclude derivatives
fi


