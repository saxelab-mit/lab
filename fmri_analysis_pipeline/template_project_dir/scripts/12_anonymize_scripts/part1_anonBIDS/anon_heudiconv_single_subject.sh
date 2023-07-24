#!/bin/bash -l

# run heudiconv container for one subject
# this script takes in args
#   $1 - project name (expected to be in /om3/group/saxelab/PROJECT)
#   $2 - subproject (for multi-study analyses. Expected in /om3/group/saxelab/PROJECT/data/SUBPROJECT
#   $3 - heudiconv file (expected to be in /om3/group/saxelab/PROJECT/scripts/heuristic_files)
#   $4 - array of subjects

#SBATCH -J heudiconv
#SBATCH -t 2:00:00
#SBATCH --mem=10GB
#SBATCH --cpus-per-task=1

heudi_file=$1
args=($@)
subjs=(${args[@]:1}) # drop initial args

proj=`cat ../../PATHS.txt`
data=$proj/data

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

subject=${subjs[${SLURM_ARRAY_TASK_ID}]}

echo "Submitted job for: ${subject}"

singularity exec -B /om:/om -B /om3:/om3 -B /nese:/nese -B /cm:/cm -H $proj/scripts $proj/singularity_images/anonymize.sif \
/neurodocker/startup.sh heudiconv \
-d $data/dicoms/{subject}/dicom/*.dcm \
-s $subject -f $proj/scripts/heuristic_files/$heudi_file \
-c dcm2niix \
-b --minmeta --overwrite \
-o $data/BIDS_anon \
--anon-cmd=$proj/scripts/lookup_anon_ID.py
