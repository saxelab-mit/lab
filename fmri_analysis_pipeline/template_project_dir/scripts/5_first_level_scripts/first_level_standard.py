"""
Individual run analysis using `fmriprep` outputs and FSL.

Adapted script from original notebook:
https://github.com/poldrack/fmri-analysis-vm/blob/master/analysis/postFMRIPREPmodelling/First%20and%20Second%20Level%20Modeling%20(FSL).ipynb

Requirement: BIDS dataset (including events.tsv), fmriprep outputs, and modeling files [more on this when concrete]

"""
import nipype.algorithms.modelgen as model
from  nipype.interfaces import fsl, ants
from nipype.interfaces.base import Bunch
from nipype import Workflow, Node, IdentityInterface, Function, DataSink, JoinNode, MapNode
import os
import os.path as op
import argparse
from bids.grabbids import BIDSLayout
from nipype.workflows.fmri.fsl.preprocess import create_susan_smooth
from nipype.algorithms import rapidart
import pandas as pd
import glob


__version__ = '0.0.1'


# use spatial smoothing? if True, kernel size is used 
run_smoothing = True
smoothing_kernel_size = 6 # i.e., 6mm FWHM kernel

def create_firstlevel_workflow(bids_dir, subj, task, fmriprep_dir, runs, outdir,
                               events, session, TR, sparse, workdir, dropvols=0,
                               name="{}_task-{}_standard_levelone"):
    """Processing pipeline"""

    # initialize workflow
    wf = Workflow(name=name.format(subj, task),
                  base_dir=workdir)
    wf.config['execution']['parameterize_dirs'] = False

    infosource = Node(IdentityInterface(fields=['run_id', 'event_file']), name='infosource')
    infosource.iterables = [('run_id', runs),
                            ('event_file', events)]
    infosource.synchronize = True

    ## print runs, events to script dir for debugging
    ## MAKE SURE TO UDPATE PATH IF USING
    #xx = pd.DataFrame(runs)
    #xx.to_csv('/nese/mit/group/saxelab/projects/EMOfd_09_2021/scripts/5_first_level_scripts/runs.txt', header=None, index=None)

    #yy = pd.DataFrame(events)
    #yy.to_csv('/nese/mit/group/saxelab/projects/EMOfd_09_2021/scripts/5_first_level_scripts/events.txt', header=None, index=None)


    def data_grabber(subj, task, fmriprep_dir, session, run_id):
        """Quick filegrabber ala SelectFiles/DataGrabber"""
        import os.path as op

        prefix = '{}_task-{}_run-{:03d}'.format(subj, task, run_id)
        fmriprep_func = op.join(fmriprep_dir, "{}".format(subj), "func")
        if session:
            prefix = '{}_ses-{}_task-{}_run-{:03d}'.format(
                subj, session, task, run_id
            )
            fmriprep_func = op.join(fmriprep_dir, "{}".format(subj),
                                    "ses-{}".format(session), "func")

        # grab these files
        confound_file = op.join(fmriprep_func, "{}_desc-confounds_timeseries.tsv".format(prefix))
        mni_file = op.join(
            fmriprep_func,
            "{}_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz".format(prefix)
        )
        
        #mni_mask = mni_file.replace("-preproc_bold.", "-brain_mask.")

        prefix_mask = '{}'.format(subj)
        if session: 
            prefix_mask = '{}_{}'.format(subj, session)

        mni_mask = op.join(
            fmriprep_func,
            "{}_MNI152NLin2009cAsym_res-2_desc-brain_mask_allruns-BOLDmask.nii.gz".format(prefix_mask)
        )


        return confound_file, mni_file, mni_mask



    datasource = Node(Function(output_names=["confound_file",
                                             "mni_file",
                                             "mni_mask"],
                               function=data_grabber),
                      name='datasource')
    datasource.inputs.subj = subj
    datasource.inputs.task = task
    datasource.inputs.fmriprep_dir = fmriprep_dir
    datasource.inputs.session = session
    wf.connect(infosource, "run_id", datasource, "run_id")
    
    #write realignment parameters in a format that art likes
    def get_mcparams(in_tsv):
        import os
        import pandas as pd
        pd.read_table(in_tsv).to_csv(
            'mcparams.tsv', sep='\t',
            columns=['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'],
            header=False, index=False)
        return os.path.abspath('mcparams.tsv')
    
    writeparams = Node(Function(output_names=["realignment_params_file"], 
                                function = get_mcparams),
                       name='writeparams')
    
    wf.connect(datasource, "confound_file", writeparams, "in_tsv")
    
    #use rapidart to detect outliers in realigned files
    art = Node(rapidart.ArtifactDetect(), name = 'art')
    art.inputs.use_differences = [True, False]
    art.inputs.use_norm = True
    art.inputs.norm_threshold = .4
    art.inputs.zintensity_threshold = 3
    art.inputs.mask_type = 'file'
    art.inputs.parameter_source = 'SPM'

    wf.connect(datasource, "mni_file", art, "realigned_files")
    wf.connect(datasource, "mni_mask", art, "mask_file")
    wf.connect(writeparams, "realignment_params_file", art, "realignment_parameters")

    
    #smooth before running model. 6mm
    if run_smoothing:
        smooth = create_susan_smooth()
        wf.connect(datasource, "mni_file", smooth, 'inputnode.in_files')
        smooth.inputs.inputnode.fwhm = smoothing_kernel_size
        wf.connect(datasource, "mni_mask", smooth, 'inputnode.mask_file')


    def gen_model_info(event_file, confound_file, regressor_names, dropvols):
        """Defines `SpecifyModel` information from BIDS events."""
        import pandas as pd
        from nipype.interfaces.base import Bunch

        events = pd.read_csv(event_file, sep="\t")
        trial_types = events.trial_type.unique()
        onset = []
        duration = []
        for trial in trial_types:
            onset.append(events[events.trial_type == trial].onset.tolist())
            duration.append(events[events.trial_type == trial].duration.tolist())

        confounds = pd.read_csv(confound_file, sep="\t", na_values="n/a")
        regressors = []
        for regressor in regressor_names:
            if regressor == 'framewise_displacement':
                regressors.append(confounds[regressor].fillna(0)[dropvols:])
            else:
                regressors.append(confounds[regressor][dropvols:])


        info = [Bunch(
            conditions=trial_types,
            onsets=onset,
            durations=duration,
            regressors=regressors,
            regressor_names=regressor_names,
        )]
        return info

    modelinfo = Node(Function(function=gen_model_info), name="modelinfo")
    modelinfo.inputs.dropvols = dropvols

    # these will likely be in bids model json in the future
    modelinfo.inputs.regressor_names = [
        'framewise_displacement',
        'a_comp_cor_00',
        'a_comp_cor_01',
        'a_comp_cor_02',
        'a_comp_cor_03',
        'a_comp_cor_04',
        'a_comp_cor_05',
    ]
    wf.connect(infosource, "event_file", modelinfo, "event_file")
    wf.connect(datasource, "confound_file", modelinfo, "confound_file")

    if dropvols:
        roi = Node(fsl.ExtractROI(t_min=dropvols, t_size=-1), name="extractroi")
        if run_smoothing:
            wf.connect(smooth, "outputnode.smoothed_files", roi, "in_file")
        else: 
            wf.connect(datasource, "mni_file", roi, "in_file")

    if sparse:
        modelspec = Node(model.SpecifySparseModel(), name="modelspec")
        modelspec.inputs.time_acquisition = None
    else:
        modelspec = Node(model.SpecifyModel(), name="modelspec")

    modelspec.inputs.input_units = "secs"
    modelspec.inputs.time_repetition = TR
    modelspec.inputs.high_pass_filter_cutoff = 210. # NOTE - THIS MAY CHANGE FOR DIFFERENT STUDIES
    wf.connect(modelinfo, "out", modelspec, "subject_info")

    if dropvols:
        wf.connect(roi, "roi_file", modelspec, "functional_runs")
    else:
        if run_smoothing: 
            wf.connect(smooth, "outputnode.smoothed_files", modelspec, "functional_runs")
        else: 
            wf.connect(datasource, "mni_file", modelspec, "functional_runs")
        
    wf.connect(art, 'outlier_files', modelspec, 'outlier_files')

    def read_contrasts(bids_dir, task):
        import os.path as op
        import pandas as pd 

        contrasts = []
        contrasts_file = op.join(bids_dir, "code", "contrasts.tsv")
        if not op.exists(contrasts_file):
            raise FileNotFoundError("Contrasts file not found.")
        #with open(contrasts_file, "r") as fp:
        #    info = [line.strip().split("\t") for line in fp.readlines()]
        info = pd.read_csv(contrasts_file, sep='\t')


        for index, row in info.iterrows():
            if row[0] != task:
                continue

            contrasts.append([
                row[1],
                "T",
                [cond for cond in row[2].split(" ")],
                [float(w) for w in row[3].split(" ")]
            ])

        if not contrasts:
            raise AttributeError("No contrasts found for task {}".format(task))
        return contrasts

    contrastgen = Node(Function(output_names=["contrasts"],
                                function=read_contrasts),
                       name="contrastgen")
    contrastgen.inputs.bids_dir = bids_dir
    contrastgen.inputs.task = task

    level1design = Node(fsl.Level1Design(), name="level1design")
    level1design.inputs.interscan_interval = TR
    level1design.inputs.bases = {"dgamma": {"derivs": False}}
    level1design.inputs.model_serial_correlations = True
    wf.connect(modelspec, "session_info", level1design, "session_info")
    wf.connect(contrastgen, "contrasts", level1design, "contrasts")

    modelgen = Node(fsl.FEATModel(), name="modelgen")
    wf.connect(level1design, "fsf_files", modelgen, "fsf_file")
    wf.connect(level1design, "ev_files", modelgen, "ev_files")

    masker = MapNode(fsl.ApplyMask(), name="masker", iterfield=['in_file'])
    wf.connect(datasource, "mni_mask", masker, "mask_file")

    if dropvols:
        wf.connect(roi, "roi_file", masker, "in_file")
    else:
        if run_smoothing: 
            wf.connect(smooth, "outputnode.smoothed_files", masker, "in_file")
        else: 
            wf.connect(datasource, "mni_file", masker, "in_file")

    glm = MapNode(fsl.FILMGLS(), name="filmgls", iterfield=['in_file'])
    if run_smoothing: 
        glm.inputs.mask_size = smoothing_kernel_size
        glm.inputs.smooth_autocorr = True
    wf.connect(masker, "out_file", glm, "in_file")
    wf.connect(modelgen, "design_file", glm, "design_file")
    wf.connect(modelgen, "con_file", glm, "tcon_file")
    wf.connect(modelgen, "fcon_file", glm, "fcon_file")


    def substitutes(contrasts):
        """Datasink output path substitutes"""
        subs = []
        for i, con in enumerate(contrasts,1):
            # replace annoying chars in filename
            name = con[0].replace(" ", "").replace(">", "_gt_").lower()

            subs.append(('/cope%d.' % i, '/con_%d_%s_cope.' % (i,name)))
            subs.append(('/varcope%d.' % i, '/con_%d_%s_varcope.' % (i,name)))
            subs.append(('/zstat%d.' % i, '/con_%d_%s_zstat.' % (i, name)))
            subs.append(('/tstat%d.' % i, '/con_%d_%s_tstat.' % (i, name)))
            subs.append(('/_filmgls0/', '/'))
        return subs


    gensubs = Node(Function(function=substitutes), name="substitute_gen")
    wf.connect(contrastgen, "contrasts", gensubs, "contrasts")

    # stats should equal number of conditions...
    sinker = Node(DataSink(), name="datasink")
    sinker.inputs.base_directory = outdir
    sinker.inputs.regexp_substitutions = [("_event_file.*run_id_", "run"),
                                          ("model/sub.*_run-", "model/run"),
                                          ("_bold_space-MNI","/MNI"),
                                          ("_space-MNI","/MNI")]

    
    wf.connect(gensubs, "out", sinker, "substitutions")
    wf.connect(modelgen, "design_file", sinker, "design.@design_file")
    wf.connect(modelgen, "con_file", sinker, "design.@tcon_file")
    wf.connect(modelgen, "design_cov", sinker, "design.@cov")
    wf.connect(modelgen, "design_image", sinker, "design.@design")
    wf.connect(glm, "copes", sinker, "model.@copes")
    wf.connect(glm, "dof_file", sinker, "model.@dof")
    wf.connect(glm, "logfile", sinker, "model.@log")
    wf.connect(glm, "param_estimates", sinker, "model.@pes")
    wf.connect(glm, "residual4d", sinker, "model.@res")
    wf.connect(glm, "sigmasquareds", sinker, "model.@ss")
    wf.connect(glm, "thresholdac", sinker, "model.@thresh")
    wf.connect(glm, "tstats", sinker, "model.@tstats")
    wf.connect(glm, "varcopes", sinker, "model.@varcopes")
    wf.connect(glm, "zstats", sinker, "model.@zstats")
    wf.connect(datasource, "mni_mask", sinker, "model.@mask_file")
    wf.connect(art, "plot_files", sinker, "design.@art_plot")
    wf.connect(art, "norm_files", sinker, "design.@art_norm")
    wf.connect(art, "outlier_files", sinker, 'design.@outlier_files')
    #fstats should be here, too?
    return wf


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument("bids_dir",
                        help="Root BIDS directory")
    parser.add_argument("-f", dest="fmriprep_dir",
                        help="Output directory of fmriprep")
    parser.add_argument("-s", dest="subjects", nargs="*",
                        help="List of subjects to process (default: all)")
    parser.add_argument("-t", dest="tasks", nargs="*",
                        help="List of tasks to process (default: all)")
    parser.add_argument("-ss", dest="session",
                        help="Session to process (default: None)")
    parser.add_argument("-w", dest="workdir", default=os.getcwd(),
                        help="Working directory")
    parser.add_argument("-o", dest="outdir", default=os.getcwd(),
                        help="Output directory")
    parser.add_argument("--sparse", action="store_true",
                        help="Specify a sparse model")
    parser.add_argument("-p", dest="plugin",
                        help="Nipype plugin to use (default: MultiProc)")
    return parser

def process_subject(layout, bids_dir, subj, task, fmriprep_dir, session, outdir, workdir, sparse):
    """Grab information and start nipype workflow
    We want to parallelize runs for greater efficiency

    """
#    runs = list(range(1, len(layout.get(subject=subj,
#                                        type="bold",
#                                        task=task,
#                                        extensions="nii.gz")) + 1))

    #This is convoluted because of a couple of bugs in the BIDSLayout. We should be able to use the layout entities directly
    #sess_file = layout.get_collections(level='session', subject=subj)
    #sess_df = sess_file[0].to_df()
    #scans_tsv = layout.get(type='scans',subject=subj, extensions='.tsv',return_type="file")[0]
    scans_tsv = glob.glob(op.join(bids_dir, subj, '*_scans.tsv'))[0]
    scans_df = pd.read_csv(scans_tsv, sep='\t')

    scans_df['task'] = scans_df['filename'].str.split('task-', expand=True).loc[:,1]
    scans_df['task'] = scans_df['task'].str.split('_run', expand=True).loc[:,0]
    scans_df['run'] = scans_df['filename'].str.split('run-', expand=True).loc[:,1]
    scans_df['run'] = scans_df['run'].str.split('_bold', expand=True).loc[:,0]
    keepruns = scans_df[(scans_df.MotionExclusion == False) & (scans_df.OtherExclusion== False) 
             & (scans_df.RepeatSubjectExclusion == False) & (scans_df.task == task)].run

    keepruns = list(keepruns.astype(int).values)


    if not keepruns:
        raise FileNotFoundError(
            "No included bold {} runs found for subject {}".format(task, subj)
        )

    #events = layout.get(subject=subj, type="events", run=keepruns, task=task, return_type="file")
    #events_all = glob.glob(op.join(bids_dir, subj, 'func', "{}_task-{}_*_events.tsv".format(subj, task)))
    #events = [evfile for evfile in events_all if any(str(run) in evfile for run in keepruns)]

    if session:
        events_all = glob.glob(op.join(bids_dir, subj, session, 'func', "{}_{}_task-{}_*_events.tsv".format(subj, session, task)))
    else:
        events_all = glob.glob(op.join(bids_dir, subj, 'func', "{}_task-{}_*_events.tsv".format(subj, task)))

    events = []

    for run in keepruns:
        ev_match = [evfile for evfile in events_all if 'run-{:03d}'.format(run) in evfile]
        events.append(ev_match[0])
    #events = [evfile for evfile in events_all if any(str(run) in evfile for run in keepruns)]
    
    # assumes TR is same across runs
    #epi = layout.get(subject=subj, type="bold", task=task, return_type="file")[0]
    epi = glob.glob(op.join(bids_dir, subj, 'func', "{}_task-{}_*_bold.nii.gz".format(subj, task)))[0]
    TR = layout.get_metadata(epi)["RepetitionTime"]

    # IF RESTING - not necessary
    # will result in entirely new pipeline...
    if not events:
        raise FileNotFoundError(
            "No event files found for subject {}".format(subj)
        )

    suboutdir = op.join(outdir, subj, task)

    wf = create_firstlevel_workflow(bids_dir, subj, task, fmriprep_dir, keepruns,
                                    suboutdir, events, session, TR, sparse, workdir)

    return wf

def main(argv=None):
    parser = argparser()
    args = parser.parse_args(argv)

    if not op.exists(args.bids_dir):
        raise IOError("BIDS directory {} not found.".format(args.bids_dir))

    fmriprep_dir = (args.fmriprep_dir if args.fmriprep_dir else
                    op.join(args.bids_dir, 'derivatives/fmriprep'))

    if not op.exists(fmriprep_dir):
        raise IOError("fmriprep directory {} not found.".format(fmriprep_dir))

    workdir, outdir = op.realpath(args.workdir), op.realpath(args.outdir)
    os.makedirs(workdir, exist_ok = True)

    layout = BIDSLayout(args.bids_dir)

    tasks = (args.tasks if args.tasks else
             [task for task in layout.get_tasks() if 'rest' not in task.lower()])
    subjects = args.subjects if args.subjects else layout.get_subjects()


    for subj in subjects:
        for task in tasks:
            wf = process_subject(layout, args.bids_dir, subj, task, fmriprep_dir,
                                 args.session, outdir, workdir, args.sparse)

            
            wf.config['execution'] = {'crashfile_format': 'txt',
                                      'remove_unnecessary_outputs': False,
                                      'keep_inputs': True}

            plugin = args.plugin if args.plugin else "MultiProc"
            args_dict = {'n_procs' : 4}
            wf.run(plugin=plugin, plugin_args = args_dict)

if __name__ == "__main__":
    main()


