import os


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where
    
    allowed template fields - follow python string module: 
    
    item: index within category 
    subject: participant id 
    seqitem: run number during scanning
    subindex: sub index within group
    """

    t1 = create_key('sub-{subject}/anat/sub-{subject}_T1w')
    VOErun = create_key('sub-{subject}/func/sub-{subject}_task-VOE_run-{item:03d}_bold')
    DOTSrun = create_key('sub-{subject}/func/sub-{subject}_task-DOTS_run-{item:03d}_bold')
    spWMrun = create_key('sub-{subject}/func/sub-{subject}_task-spWM_run-{item:03d}_bold')
    Motionrun = create_key('sub-{subject}/func/sub-{subject}_task-Motion_run-{item:03d}_bold')	

    info = {t1: [], VOErun: [], DOTSrun: [],  spWMrun: [], Motionrun: []}

    for s in seqinfo:
        if ('MPRAGE' in s.protocol_name) and ('NORM' in s.image_type):
            info[t1] = [s.series_id]
        if (s.dim4 == 210) and (not s.is_motion_corrected):
            info[VOErun].append({'item': s.series_id})
        if (s.dim4 == 248) and (not s.is_motion_corrected):
            info[DOTSrun].append({'item': s.series_id})
        if (s.dim4 == 224) and (not s.is_motion_corrected):
            info[spWMrun].append({'item': s.series_id})
        if (s.dim4 >= 130) and ('MotionLoc'in s.protocol_name) and (not s.is_motion_corrected):
            info[Motionrun].append({'item': s.series_id})

    return info
