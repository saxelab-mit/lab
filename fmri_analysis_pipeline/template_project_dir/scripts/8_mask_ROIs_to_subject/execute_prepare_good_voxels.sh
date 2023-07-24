#!/bin/bash -l
#SBATCH -t 2:00:00
#SBATCH -N 1
#SBATCH -c 24
#SBATCH --mem=35G
#SBATCH -p saxelab

proj=`cat ../PATHS.txt`

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

singularity exec --cleanenv -B /om:/om -B /om3:/om3 -B /cm:/cm -B /nese:/nese $proj/singularity_images/magnitude_extraction_extended_latest.sif /neurodocker/startup.sh runipy $proj/scripts/8_mask_ROIs_to_subject/prepare_good_voxel_ROIs.ipynb
