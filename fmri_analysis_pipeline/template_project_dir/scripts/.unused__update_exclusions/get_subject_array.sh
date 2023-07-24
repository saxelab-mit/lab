#!/bin/bash 

# purpose: get an array of subjects to run a job array through SLURM for a specific preproc/analysis step of the EMOfd pipeline 
# uses the exclusions.csv file that lives in data dir
# author: kolydic
# date: aug 16, 2021
# input args:   (1) which exclusions list (i.e. what column to draw from)
#		(2) use original subject names, BIDS subject names, or BIDS with 'sub-' as prefix	
# returns: an array of subject IDs to be used in the job array


# input args (1): heudiconv, fmriprep, markmotion, firstlevel, secondlevel, 
# 		  tier, univariate, multivariate, wholebrain, permutationtest


# input args (2): 1 -> SAXE_EMOfd_01 
#		  2 -> sub-SAXEEMOfd01    
#		  3 -> SAXEEMOfd01 



currentstep=$1
id_type=$2

project_dir=/nese/mit/group/saxelab/projects/EMOfd
exclusions_CSV=$project_dir/data/exclusions.csv

declare -ga subjectlist
while IFS=, read -r id_col BIDSid_col failcode_col heudiconv_col fmriprep_col markmotion_col firstlevel_col secondlevel_col tier_col univariate_col multivariate_col wholebrain_col permutationtest_col

do 
	if [ "$id_type" = "1" ]; then
		subj=$id_col
	elif [ "$id_type" = "2" ]; then
		subj=$BIDSid_col
	elif [ "$id_type" = "3" ]; then
		subj=${BIDSid_col:4:$((${#BIDSid_col}))}
	fi 

	selected_column_base=`echo $(eval echo ${currentstep}_col)`
	selected_column=`echo ${!selected_column_base}`

	if [ "$selected_column" = "0" ]; then	
		subjectlist[${#subjectlist[@]}]=$subj
	fi 

done < $exclusions_CSV 

printf "%s\n" "${subjectlist[@]}"  > $project_dir/scripts/exclusions/subjectlist_active.txt 

