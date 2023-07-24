# Usage: 
    # if you want to anonymize dates:
        # singularity exec -B /om:/om -B /om3:/om3 /om3/group/saxelab/$proj/singularity_images/anonymize.sif python anonymize_part4_scans.py $proj true Buckner
    # if not:
        # singularity exec -B /om:/om -B /om3:/om3 /om3/group/saxelab/$proj/singularity_images/anonymize.sif python anonymize_part4_scans.py $proj false

import pandas as pd
import glob
import os.path as op
import datetime as dt
from dateutil.relativedelta import relativedelta
import sys

projdir = sys.argv[1]
anonymize_scandates = sys.argv[2].lower() == 'true'
# operator argument not used right now
if len(sys.argv) > 3:
    operator = sys.argv[3]
else:
    operator = 'Unnamed'
    
subs = glob.glob(projdir + '/data/BIDS_anon/sub-*')

for sub in subs:
    print('working on subject: ' + sub)
    if anonymize_scandates:
        sub_base = op.basename(sub)
        scans_fname = op.join(sub, sub_base + '_scans.tsv')
        
        df = pd.read_csv(scans_fname, sep="\t")
        
        fake_acq_time = dt.datetime.strptime('2000-01-01T00:00:00',"%Y-%m-%dT%H:%M:%S")
        fake_acq_time_str = dt.datetime.strftime(fake_acq_time,"%Y-%m-%dT%H:%M:%S")
        
        for i, row in df.iterrows():
            fake_time = dt.datetime.strftime(fake_acq_time,"%Y-%m-%dT%H:%M:%S")
            df.loc[i, 'acq_time'] = fake_time
            fake_acq_time = fake_acq_time + relativedelta(seconds=1)
        
        df.to_csv(scans_fname, sep = '\t', index = False)
        print('anonymized scan dates for ' + sub)

    # Do this in any case
    sub_base = op.basename(sub)
    scans_fname = op.join(sub, sub_base + '_scans.tsv')
    df = pd.read_csv(scans_fname, sep="\t")

    anat_files = glob.glob(sub + '/anat/*.nii.gz')
    for a in anat_files:
        # checking whether files were defaced
        if '_defaced' not in op.basename(a):
            print("You haven't defaced {} yet. Go back and run anonymize_part3_pydeface.sh".format(op.basename(a)))
        else:
            # if file was defaced, then replace the filename in scans.tsv
            undefaced_file = op.basename(a).replace('_defaced', '')
            defaced_file = op.basename(a)
            df.loc[df['filename'] == 'anat/' + undefaced_file, "filename"] = 'anat/' + defaced_file
            print('replaced anatomical name in scans file for ' + sub)

    df.to_csv(scans_fname, sep="\t", index=False)
            
        
        
        
    

