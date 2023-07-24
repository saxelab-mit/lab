#!/bin/bash -l


#SBATCH -J heudiconv
#SBATCH -t 1:00:00
#SBATCH --mem=10GB
#SBATCH --cpus-per-task=1
#SBATCH --partition=saxelab

#purpose: run heudiconv for one subject 


# THIS SCRIPT IS INTENDED TO BE RUN THROUGH THE WRAPPER SCRIPT submit_heudiconv_array.sh 
# THE JOB ARRAY WRAPPER SCRIPT CAN ALSO BE USED FOR SINGLE SUBJECT


heudi_file=$1
study_root=`cat ../PATHS.txt`


subjs=("${@:2}")

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

subject=${subjs[${SLURM_ARRAY_TASK_ID}]}

echo "Submitted job for: ${subject}"

singularity exec -B /om3:/om3 -B /cm:/cm -B /om2:/om2 -B /om:/om -B /mindhive:/mindhive -B /nese:/nese $study_root/singularity_images/heudiconv_0.9.0.sif \
/neurodocker/startup.sh heudiconv \
-d $study_root/data/dicoms/{subject}/dicom/*.dcm \
-s $subject -f $study_root/scripts/1_heudiconv_scripts/$heudi_file \
-c dcm2niix -o $study_root/data/BIDS \
-b --minmeta --overwrite


