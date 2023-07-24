#!/bin/bash

# Script adapted from Martin M Monti (monti@psych.ucla.edu)
# Takes X Y and Z coordinates in FSL space (**not MNI space**), and produces a spherical ROI of mm radius
# INPUTS:
# image = image that has the same resolution as the image you want to apply the ROI to (e.g. avg152T1_brain.nii.gz from Saxelab standard pipeline)
# NOTE: this image either has to be in the folder you are launching the command from, or has to have a full path.
# X Y Z = coordinates in FSL space of the center of the ROI
# mm = radius of the ROI in mm
# ROIname = what you'd like to call this ROI (e.g. RSTS)
# example usage: ./make_sphere_roi.sh avg152T1_brain.nii.gz 21 43 43 10 STS

echo "******************************"
echo "Input image: ${1} "
echo "ROI center FSL coordinates: x = ${2},  y = ${3}, z = ${4} "
echo "ROI size: ${5} mm"
echo "ROI name: ${6}"

proj=/om2/group/saxelab/NES_fMRI
write_dir=$proj/TIER/analysis_data/ROI_MASKS/sphere_ROIs/spheres
echo "Project dir: ${proj} "

fslmaths ${1} -roi $2 1 $3 1 $4 1 0 1 ${write_dir}/tmp_point_mask
fslmaths ${write_dir}/tmp_point_mask -kernel sphere $5 -fmean -thr 1e-4 -bin ${write_dir}/${6}_${2}-${3}-${4}_${5}mm_thrbin -odt float
rm ${write_dir}/tmp_point_mask.*
echo "Done! The output file is called '${6}_${2}-${3}-${4}_${5}mm_thrbin' "
echo " " 
