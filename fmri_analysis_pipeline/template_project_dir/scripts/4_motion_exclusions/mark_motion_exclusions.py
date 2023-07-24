from bids.grabbids import BIDSLayout
import bids.variables.kollekshuns
import pandas as pd
from shutil import copyfile
import numpy as np
from collections import defaultdict
import os.path as op
import sys
import glob
import os

## SEE SECTION MARKED TO CHANGE FOR YOUR STUDY! 

def mark_motion_exclusions(study, sub):

    data_dir="%s/data/BIDS/"%study
    layout = BIDSLayout(data_dir)

    #Find the BIDS scans file and make a backup before we start mucking with it
    scansfiles = glob.glob(op.join(data_dir, '*' + sub, '*_scans.tsv'))
    scansfile = scansfiles[0]

    # copy original scansfiles to a hidden directory in data/ instead of in BIDS
    # (.orig files are not BIDS compatible)
    scansfile_base = op.basename(scansfile)
    copy_orig_dir = op.join(study, 'data/.scansfiles_orig')
    if not op.exists(copy_orig_dir):
        os.makedirs(copy_orig_dir)
    copy_orig_scansfile_path = op.join(copy_orig_dir, scansfile_base)
    if ~op.isfile(copy_orig_scansfile_path + '.orig'):
        copyfile(scansfile, copy_orig_scansfile_path + '.orig')

    #Read the TSV file into a dataframe, the parsed session info into a dataframe (which has granular task info, etc, 
    # but is lacking the anatomical file), then create one useful dataframe
    df_tsv = pd.read_csv(scansfile, sep='\t')
   
    df_tsv['task'] = df_tsv['filename'].str.split('task-', expand=True).loc[:,1]
    df_tsv['task'] = df_tsv['task'].str.split('_run', expand=True).loc[:,0]
    df_tsv['run'] = df_tsv['filename'].str.split('run-', expand=True).loc[:,1]
    df_tsv['run'] = df_tsv['run'].str.split('_bold', expand=True).loc[:,0]
    df_tsv['subject'] = df_tsv['filename'].str.split('func/', expand=True).loc[:,1]
    df_tsv['subject'] = df_tsv['subject'].str.split('_task', expand=True).loc[:,0]

    df_merge = df_tsv
    df_merge.loc[:,'MotionExclusion'] = False
    df_merge.loc[:,'MeanFD'] = None
    df_merge.loc[:,'RepeatSubjectExclusion'] = False
    df_merge.loc[:,'OtherExclusion'] = False
    df_merge.loc[:, 'OtherExclusionReason'] = None

    for index, row in df_merge.iterrows():
        if  not pd.isnull(row['run']):
            task = row['task']
            run=int(row['run'])
            subject = row['subject']
            filestr = 'func/*task-' + task + '_run-*' + str(run) + '_desc-confounds*.tsv'
            f = glob.glob(op.join(data_dir, 'derivatives/fmriprep', '*' + subject, filestr))
            confound_file = f[0]

            #Load into pandas
            dfConfounds = pd.read_csv(confound_file,sep='\t')

            #Extract FD and calculate TRs over .4 FD limit
            FD = dfConfounds.framewise_displacement[1:]
            FDoverlim = FD > .4

            #sum of bools is number of true values. count of bool array is length
            meanFD = np.mean(FD)
            df_merge.loc[index, 'MeanFD'] = meanFD
            if (FDoverlim.sum() / FDoverlim.count()) >= .25:
                df_merge.loc[index, 'MotionExclusion'] = True
                print('Motion Exclusion: ' + row['filename'])


    df_merge.to_csv(scansfile,sep = '\t', 
                    index=False, 
                    columns=['filename', 'acq_time', 'operator', 'randstr', 'MotionExclusion', 'MeanFD',
                             'RepeatSubjectExclusion','OtherExclusion', 'OtherExclusionReason'])


    logfile = study + '/data/BIDS/' + sub + '/' + sub + '_scans.tsv'
    subj_scans = pd.read_csv(logfile, sep='\t')


def main():
    study = sys.argv[1]
    subj = sys.argv[2]
    print('Marking motion exclusions in scans.tsv file for ' + subj + ' in study: ' + study)
    mark_motion_exclusions(study, subj)
    
if __name__ == '__main__':
    main()
