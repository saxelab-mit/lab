
from nilearn import plotting
from nilearn import image
from nilearn import masking
import nilearn
import argparse
import pandas as pd
import numpy as np

import os.path as op
import os
import glob

def concat_masks(fmriprep_dir, subjID, session=None): 

    subj = op.join(fmriprep_dir, subjID)

    print('SUBJECT', subj)

    #subj_label = op.basename(subj[0:-1])

    if session: 
        # path to inputs 
        subdir = op.join(subj, session, 'func')
        # output path
        concat_img_fname = '{}/{}_{}_MNI152NLin2009cAsym_res-2_desc-brain_mask_allruns-BOLDmask.nii.gz'.format(subdir, subjID, session)
    else: 
        subdir = op.join(subj, 'func')
        concat_img_fname = '{}/{}_MNI152NLin2009cAsym_res-2_desc-brain_mask_allruns-BOLDmask.nii.gz'.format(subdir, subjID)

    maskfiles = glob.glob(op.join(subdir, '*_desc-brain_mask.nii.gz'))  


    if len(maskfiles) == 0:
        print('NO BRAIN MASKS FOUND FOR THIS SUBJECT')

    else:
        basemask = maskfiles[0]
        basemask_img = image.load_img(basemask)
        concat_mask_img = basemask_img 


        if len(maskfiles) > 1:
            for maskI in range(1, len(maskfiles)):
                mask_img = image.load_img(maskfiles[maskI])
                concat_mask_img = image.math_img("img1 + img2", img1 = concat_mask_img, img2 = mask_img)

        ## BINARIZE HERE 
            
        concat_mask_data = concat_mask_img.get_fdata()
        concat_mask_data[concat_mask_data >= 1] = 1
        concat_mask_img_bin = image.new_img_like(basemask_img, concat_mask_data)
        
        #concat_img_fname = '{}/{}_{}_space-MNI152NLin2009cAsym_res-2_desc-brain_mask_ALLRUNS.nii.gz'.format(subdir, subj_label, unique_task)
        
        concat_mask_img_bin.to_filename(concat_img_fname)
        print('CONCATENATED MASK SAVED TO: {}'.format(concat_img_fname))


def argparser():
    parser = argparse.ArgumentParser()
    #parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument("-f", dest="fmriprep_dir",
                        help="Output directory of fmriprep")
    parser.add_argument("-s", dest="subjID",
                        help="subject ID")                
    parser.add_argument("-ss", dest="session", default=None,
                        help="Session to process (default: None)")
    return parser


def main(argv=None):
    parser = argparser()
    args = parser.parse_args(argv)

    if not op.exists(args.fmriprep_dir):
        raise IOError("fMRIprep directory {} not found.".format(args.fmriprep_dir))

    if not args.session == None:
        concat_masks(args.fmriprep_dir, args.subjID, args.session) 
    else:
        concat_masks(args.fmriprep_dir, args.subjID)


if __name__ == "__main__":
    main()
