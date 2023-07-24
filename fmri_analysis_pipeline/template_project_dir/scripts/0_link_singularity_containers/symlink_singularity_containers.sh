#!/bin/bash


# CREATE SYMBOLIC LINKS FROM /om3/group/saxelab/LAB_STANDARD_fMRI_CODE : 
# we want singularity images accessible but we don't want a bunch of copies
# so this creates a symbolic link, like a shortcut or pointer
# for all the content of the lab standard containers 
# and puts those links in your project folder


## THIS SCRIPT REQUIRES THAT YOU HAVE ALREADY UPDATED PATHS.txt IN THE SCRIPTS FOLDER
## THIS SCRIPT NEEDS TO BE RUN ONLY ONCE WHEN SETTING UP YOUR PROJECT FOLDER



study_root=`cat ../PATHS.txt`

masterdir_containers="/om3/group/saxelab/LAB_STANDARD_fMRI_CODE/singularity_images_master"

studydir_containers="$study_root/singularity_images"

if [[ ! -e $studydir_containers ]]; then \
 mkdir $studydir_containers; \
else echo "singularity containers dir already exists for project folder"; \
fi

if [ -z "$(ls -A $studydir_containers)" ]; then \
 ln -s $masterdir_containers/*.* $studydir_containers/; \
 echo "symbolically linking singularity containers"; \
else echo "singularity containers dir is not empty, aborting"; \
fi
