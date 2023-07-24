#!/bin/bash -l
#SBATCH --gres=gpu:1
#SBATCH --constraint=any-gpu
#SBATCH -t 30:00:00
#SBATCH -N 1
#SBATCH -c 24
#SBATCH --mem=35G

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

proj=`cat ../PATHS.txt`

singularity exec --cleanenv -B /om3:/om3 -B /nese:/nese -B /cm:/cm $proj/singularity_images/univariate_general.sif /neurodocker/startup.sh python $proj/scripts/10_multivariate_analysis_scripts/multivariate_correlation_and_distance.py
