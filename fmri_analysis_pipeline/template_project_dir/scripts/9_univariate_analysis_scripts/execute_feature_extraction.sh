#!/bin/bash -l
#SBATCH -t 48:00:00
#SBATCH -N 1
#SBATCH -c 24
#SBATCH --mem=40G
#SBATCH -p saxelab

proj=`cat ../PATHS.txt`

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

singularity exec --cleanenv -B /om:/om -B /om3:/om3 -B /cm:/cm -B /nese:/nese $proj/singularity_images/univariate_general.sif /neurodocker/startup.sh python $proj/scripts/9_univariate_analysis_scripts/feature_selection_tests.py
