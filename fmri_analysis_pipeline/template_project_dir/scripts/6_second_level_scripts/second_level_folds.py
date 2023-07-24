
"""
Individual and (group level?) analysis using `fmriprep` outputs and FSL.

Adapted script from original notebook:
https://github.com/poldrack/fmri-analysis-vm/blob/master/analysis/postFMRIPREPmodelling/First%20and%20Second%20Level%20Modeling%20(FSL).ipynb

Requirement: BIDS dataset (including events.tsv), fmriprep outputs, and modeling files [more on this when concrete]

"""
# from niflow.nipype1.workflows.fmri.fsl import create_fixed_effects_flow
from nipype.workflows.fmri.fsl import create_fixed_effects_flow
from nipype.interfaces import fsl
import nipype.interfaces.io as nio
from nipype import Workflow, Node, MapNode, IdentityInterface, Function, DataSink, JoinNode, SelectFiles
import os
import os.path as op
import argparse
import glob
from bids import BIDSLayout

__version__ = '0.0.1'

def create_secondlevel_workflow(leaveoneout, fold, num_run, firstlevel_dir, bids_dir, subj, task, outdir, 
                                workdir, name="{}_task-{}_leveltwo"):
    """Processing pipeline"""
    # initialize workflow
    wf = Workflow(name=name.format(subj, task), 
                  base_dir=workdir)

    def get_runs(subj, task, firstlevel_dir):
        from nipype import SelectFiles, Node

        templates = {'run': '{subj}/{task}/model/run*'}
        gr = Node(SelectFiles(templates),
                  name='selectfiles')
        gr.inputs.base_directory = firstlevel_dir
        gr.inputs.subj = subj
        gr.inputs.task = task
        return gr.run().outputs

    def get_data_from_run(run):
        from nipype import SelectFiles, Node

        templates = {'dof': 'dof',
                     'copes': '*_cope.nii.gz',
                     'varcopes': '*_varcope.nii.gz',
                     #'maskfile': '*mask.nii.gz'
                     'maskfile': '../*allruns-BOLDmask.nii.gz'
                    }
        sf = Node(SelectFiles(templates),
                  name='selectfiles')

        sf.inputs.base_directory = run
        return sf.run().outputs

    def read_contrasts(bids_dir, task):
        """potential BUG? This will not update if contrasts file is changed."""
        import os.path as op

        contrasts = []
        contrasts_file = op.join(bids_dir, "code", "contrasts.tsv")
        if not op.exists(contrasts_file):
            raise FileNotFoundError("Contrasts file not found.")
        with open(contrasts_file, "r") as fp:
            info = [line.strip().split("\t") for line in fp.readlines()]

        for row in info:
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
    
    def substitutes(leaveoneout, contrasts, num_run, fold):
        """Datasink output path substitutes"""
        subs = []
        for i, con in enumerate(contrasts):
            # replace annoying chars in filename
            name = con[0].replace(" ", "").replace(">", "_gt_").lower()
            
            if leaveoneout:
                subs.append(('_flameo%d/cope1.' % i, 'fold_%i_exclude_%s_con_%i_%s_cope.' % (fold,num_run,i+1,name)))
                subs.append(('_flameo%d/varcope1.' % i, 'fold_%i_exclude_%s_con_%i_%s_varcope.' % (fold,num_run,i+1,name)))
                subs.append(('_flameo%d/zstat1.' % i, 'fold_%i_exclude_%s_con_%i_%s_zstat.' % (fold,num_run,i+1,name)))
                subs.append(('_flameo%d/tstat1.' % i, 'fold_%i_exclude_%s_con_%i_%s_tstat.' % (fold,num_run,i+1,name)))
                subs.append(('_flameo%d/mask.' % i, 'fold_%i_exclude_%s_con_%i_%s_mask.' % (fold,num_run,i+1,name)))
            else:
                subs.append(('_flameo%d/cope1.' % i, 'con_%i_%s_cope.' % (i+1,name)))
                subs.append(('_flameo%d/varcope1.' % i, 'con_%i_%s_varcope.' % (i+1,name)))
                subs.append(('_flameo%d/zstat1.' % i, 'con_%i_%s_zstat.' % (i+1,name)))
                subs.append(('_flameo%d/tstat1.' % i, 'con_%i_%s_tstat.' % (i+1,name)))
                subs.append(('_flameo%d/mask.' % i, 'con_%i_%s_mask.' % (i+1,name)))
        return subs
    
    # fixed_effects to combine stats across runs
    fixed_fx = create_fixed_effects_flow()

    sub_runs = get_runs(subj, task, firstlevel_dir)                  
    copes=[]
    varcopes=[]
    dofs=[]
    maskfiles=[]
    included_runs=[]

    if type(sub_runs.run) is str:
        sub_runs.run=[sub_runs.run]
    
    # Remove the excluded run, unless it's the last run
    if not num_run == "none":
        sub_runs.run = [path for path in sub_runs.run if not path.endswith(num_run)]
    
    for run in sub_runs.run:
        included_runs.append(run)
        newrun=get_data_from_run(run)
        if type(newrun.copes) == str:
            newcopes = [newrun.copes]
            newvarcopes = [newrun.varcopes]
        else:
            newcopes = newrun.copes
            newvarcopes = newrun.varcopes

        copes.append(newcopes)
        varcopes.append(newvarcopes)
        dofs.append(newrun.dof)
        maskfiles.append(newrun.maskfile)


    fixed_fx.get_node("l2model").inputs.num_copes = len(included_runs)
    fixed_fx.get_node("flameo").inputs.mask_file = maskfiles[0]

    # use the first mask since they should all be in same space
    
    zcopes = [list(cope) for cope in zip(*copes)]
    zvarcopes = [list(varcope) for varcope in zip(*varcopes)]
    fixed_fx.inputs.inputspec.dof_files = dofs
    fixed_fx.inputs.inputspec.copes=zcopes
    fixed_fx.inputs.inputspec.varcopes=zvarcopes


    contrastgen = Node(Function(output_names=["contrasts"],
                                function=read_contrasts),
                       name="contrastgen")
    contrastgen.inputs.bids_dir = bids_dir
    contrastgen.inputs.task = task

    gensubs = Node(Function(function=substitutes), name="substitute-gen")
    wf.connect(contrastgen, "contrasts", gensubs, "contrasts")
    gensubs.inputs.num_run = num_run
    gensubs.inputs.fold = fold
    gensubs.inputs.leaveoneout = leaveoneout

    # stats should equal number of conditions...
    sinker = Node(DataSink(), name="datasink")
    sinker.inputs.base_directory = outdir
    sinker.inputs.regexp_substitutions = [("_event_file.*run_id_", "run")]
    
    dg = nio.DataGrabber(infields=['dir'],sort_filelist=True)
    dg.inputs.base_directory="/"
    dg.inputs.template = "%s/mask*"
    datasource = Node(dg, name="datasource")

    templates = {'mask': '*'}
    gr = Node(SelectFiles(templates), name='selectfiles')

    wf.connect(gensubs, "out", sinker, "substitutions")
    
    wf.connect(fixed_fx, "outputspec.zstats", sinker, "stats.mni.@zstats")
    wf.connect(fixed_fx, "outputspec.copes", sinker, "stats.mni.@copes")
    wf.connect(fixed_fx, "outputspec.tstats", sinker, "stats.mni.@tstats")
    wf.connect(fixed_fx, "outputspec.varcopes", sinker, "stats.mni.@varcopes")
    
    wf.connect(fixed_fx, "flameo.stats_dir", datasource, "dir")
    wf.connect(datasource, "outfiles", sinker, "stats.mni.@maskfiles")
    
    return wf

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument("bids_dir",
                        help="Root BIDS directory")
    parser.add_argument("firstlevel_dir",
                        help="Location of first level analyses")
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
    parser.add_argument("-l", dest="leaveoneout", default=False,
                        help="Run leave-one-out-folds")
    parser.add_argument("--sparse", action="store_true",
                        help="Specify a sparse model")
    parser.add_argument("-p", dest="plugin",
                        help="Nipype plugin to use (default: MultiProc)")
    return parser

def process_subject(leaveoneout, fold, num_run, layout, bids_dir, firstlevel_dir, subj, task, session, outdir, workdir, sparse):
    """Grab information and start nipype workflow
    We want to parallelize runs for greater efficiency

    """
    suboutdir = op.join(outdir, subj, task)

    wf = create_secondlevel_workflow(leaveoneout, fold, num_run, firstlevel_dir, bids_dir, subj, task,
                                    suboutdir, workdir)

    return wf

def main(argv=None):
    parser = argparser()
    args = parser.parse_args(argv)

    if not op.exists(args.bids_dir):
        raise IOError("BIDS directory {} not found.".format(args.bids_dir))

    if not op.exists(args.firstlevel_dir):
        raise IOError("first level directory {} not found.".format(args.firstlevel_dir))

    workdir, outdir = op.realpath(args.workdir), op.realpath(args.outdir)
    os.makedirs(workdir, exist_ok = True)

    layout = BIDSLayout(args.bids_dir)

    tasks = (args.tasks if args.tasks else
             [task for task in layout.get_tasks() if 'rest' not in task.lower()])
    subjects = args.subjects if args.subjects else layout.get_subjects()[2:]

    leaveoneout = args.leaveoneout.lower() == 'true'
    
    for subj in subjects:     
        for task in tasks:
            # If there are 4 runs for a subject, task, output array [run1, run2, run3, run4, none]
            if leaveoneout:
                path = os.path.join(args.firstlevel_dir, subj, task, "model")
                runs = [name for name in os.listdir(path) if name.startswith('run')]
            else:
                runs = []
                
            fold = 1
            runs.append("none")
            
            for num_run in runs:
                wf = process_subject(leaveoneout, fold, num_run, layout, args.bids_dir, args.firstlevel_dir, subj, task,
                                     args.session, outdir, workdir, args.sparse)


                wf.config['execution'] = {'crashfile_format': 'txt',
                                          'remove_unnecessary_outputs': False,
                                          'keep_inputs': True}

                plugin = args.plugin if args.plugin else "MultiProc"
                wf.run(plugin=plugin)
                fold += 1

if __name__ == "__main__":
    main()


