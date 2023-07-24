proj=/nese/mit/group/saxelab/projects/EMOfd

singularity exec -B /om3:/om3 -B /om:/om -B /nese:/nese \
$proj/singularity_images/nipype_env.simg \

# use: sh /nese/mit/group/saxelab/projects/EMOfd/scripts/exclusions/update_exclusions.sh '04' 'firstlevel' 

/neurodocker/startup.sh python $proj/scripts/exclusions/update_exclusions.py $1 $2
