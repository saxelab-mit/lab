#!/bin/bash

#SBATCH -J openneuro_upld
#SBATCH -t 48:00:00
#SBATCH --mem=35GB


# HOW TO RUN THIS SCRIPT
# sbatch submitjob_openneuro_upload.sh 


#Notes: 
# make sure to change the dataset_path to your BIDS_anon dataset path!
# the -i flag in the openneuro call below ignores BIDS validation. You should have already checked that your dataset passes BIDS validation via the OpenNeuro website. 
 
# if the job times out, please try to increase the -t time requested to 72:00:00 (72 hrs) - if you cannot because of openmind policies, ask Shaohao or OM techs for help! 

proj=`cat ../PATHS.txt`
dataset_path=$proj/data/BIDS_anon

module load openmind8/apptainer/1.1.7

singularity_image=/om3/group/saxelab/LAB_STANDARD_fMRI_CODE/singularity_images_master/openneuro-cli_latest.sif


singularity exec --cleanenv -B /om:/om -B /om2:/om2 -B /om3:/om3 -B /nese:/nese -B /home/$(whoami):/home/$(whoami) $singularity_image openneuro upload -i $dataset_path



