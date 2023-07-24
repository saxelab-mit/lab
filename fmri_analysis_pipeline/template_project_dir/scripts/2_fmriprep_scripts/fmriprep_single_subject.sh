#!/bin/bash -l
#SBATCH --time=2-00:00:00
#SBATCH --mem=80GB
#SBATCH --cpus-per-task=8
#SBATCH -J fmriprep
#SBATCH -x node[054-060,100-115]

#purpose: run fmriprep container for one subject

# THIS SCRIPT IS INTENDED TO BE RUN THROUGH THE WRAPPER SCRIPT submit_fmriprep_job_array.sh 
# THE JOB ARRAY WRAPPER SCRIPT CAN ALSO BE USED FOR SINGLE SUBJECT

source /etc/profile.d/modules.sh
module use /cm/shared/modulefiles
module load openmind8/apptainer/1.1.7

set -eu
proj=`cat ../PATHS.txt`
prep_version="22.0.2"
fs_version="7.2"
IMG=$proj/singularity_images/fmriprep_${prep_version}.img


args=($@)
# assign BIDS directory
bids_dir=$1
subjs=(${args[@]:1})
# index slurm array to grab subject
subject=${subjs[${SLURM_ARRAY_TASK_ID}]}

export SINGULARITYENV_TEMPLATEFLOW_HOME=/om3/group/saxelab/LAB_STANDARD_fMRI_CODE/singularity_images_master/templateflow
export TEMPLATEFLOW_HOME=/om3/group/saxelab/LAB_STANDARD_fMRI_CODE/singularity_images_master/templateflow
unset SUBJECTS_DIR

# assign output directories
fmriprep_outdir=${bids_dir}/derivatives/fmriprep/
freesurfer_outdir=${bids_dir}/derivatives/freesurfer/
mkdir -p ${freesurfer_outdir}
mkdir -p ${fmriprep_outdir}
# Make single-subject BIDS folder in scratch
scratch=/om2/scratch/tmp/$(whoami)/fmriprep/$subject
mkdir -p ${scratch}/data/derivatives
cp -nr ${bids_dir}/$subject/ $scratch/data/
cp -n  ${bids_dir}/*.json $scratch/data/
# Remove temp freesurfer files
rm -f $scratch/data/derivatives/freesurfer/scripts/*Running*

# Define and run fMRIPrep
cmd="singularity exec -B ${scratch} -B /om:/om -B /om3:/om3 -B /cm:/cm -B /om2:/om2 -B /nese:/nese $IMG fmriprep $scratch/data $scratch/data/derivatives participant --participant_label $subject --output-spaces MNI152NLin6Asym:res-2 --cifti-output 91k --use-aroma --mem-mb 79500 -w $scratch --notrack --fs-license-file /cm/shared/openmind/freesurfer/6.0.0/.license --output-layout legacy"
echo "Submitted job for: ${subject}"
echo $'Command :\n'${cmd}
${cmd}

# Move data after successful run
cp -rn ${scratch}/data/derivatives/fmriprep/$subject $fmriprep_outdir/
cp -n ${scratch}/data/derivatives/fmriprep/$subject.html $fmriprep_outdir/
cp -n ${scratch}/data/derivatives/fmriprep/*.json $fmriprep_outdir/
cp -rn ${scratch}/data/derivatives/freesurfer/$subject $freesurfer_outdir/
