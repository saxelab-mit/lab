#!/bin/bash -l

#SBATCH -J anondate
#SBATCH -t 0:05:00
#SBATCH --mem=10GB
#SBATCH --cpus-per-task=1


# usage: sbatch submit_job_anonymize_dates.sh true
# usage: sbatch submit_job_anonymize_dates.sh false

# usage note: true/false indicates whether to anonymize scan dates;
# if false, only does step 2: rename defaced anat files as "_defaced"

projdir=`cat ../../PATHS.txt`
anonDates=$1

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

singularity exec --cleanenv -B /cm:/cm -B /nese:/nese -B /om:/om -B /om2:/om2 -B /om3:/om3 $projdir/singularity_images/anonymize.sif python $projdir/scripts/12_anonymize_scripts/part4_anonDates/anonymize_part4_scans.py $projdir $anonDates

