#!/bin/bash

bidsanon=$1
subject=$2

cd $bidsanon/$subject/anat

for x in *w.nii.gz; do
    if [[ $x == "*w.nii.gz"  ]]; then
        echo "already defaced $subject, no undefaced file present"
        continue
    fi
    echo defacing $subject now
    pydeface "$x"
    if ls *defaced.nii.gz 1> /dev/null 2>&1; then # if defaced file does exist
        echo file defaced successfully, removing original file
        rm -f "$x"
    fi
done
