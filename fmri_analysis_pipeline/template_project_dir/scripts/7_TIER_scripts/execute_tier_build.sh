#!/bin/bash -l
#SBATCH --gres=gpu:1
#SBATCH --constraint=any-gpu
#SBATCH -t 24:00:00
#SBATCH -N 1
#SBATCH -c 24
#SBATCH --mem=25G

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

proj=`cat ../PATHS.txt`

singularity exec --cleanenv -B /nese:/nese -B /om3:/om3 -B /cm:/cm $proj/singularity_images/magnitude_extraction_extended_latest.sif /neurodocker/startup.sh runipy $proj/scripts/7_TIER_scripts/tier_build_template_dir.ipynb
