
### fmri_analysis
These are the scripts for the entire fmri analysis pipeline, in python and bash:

* Converting from raw DICOMS to run-separated data in BIDS specification
* Preprocessing (
  * Separating brain from skull, calculating brain tissue segmentation, spatial normalization
  * Motion correction
  * Confound estimation
* First-level modeling
* Subject-level modeling
* Group-level modeling


There are non-standard but template scripts for: 
univariate ROI analyses 
multivariate ROI analyses 

And information regarding FLAME and RANDOMISE methods of group-level / whole-brain analyses


Also in this repository are the scripts that can be used for anonymization of an fMRI dataset. For details, see the data sharing wiki: 
https://github.mit.edu/Saxelab/lab/wiki/Data-Sharing-Cookbook 

