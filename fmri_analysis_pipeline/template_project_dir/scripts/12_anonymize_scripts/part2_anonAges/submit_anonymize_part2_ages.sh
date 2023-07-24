#!/bin/bash -l

#SBATCH -J anondate
#SBATCH -t 0:25:00
#SBATCH --mem=10GB
#SBATCH --cpus-per-task=1


# usage: sbatch submit_anonymize_part2_ages.sh


projdir=`cat ../../PATHS.txt`

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

singularity exec --cleanenv -B /cm:/cm -B /nese:/nese -B /om:/om -B /om2:/om2 -B /om3:/om3 $projdir/singularity_images/anonymize.sif python $projdir/scripts/12_anonymize_scripts/part2_anonAges/anonymize_part2_ages.py $projdir

