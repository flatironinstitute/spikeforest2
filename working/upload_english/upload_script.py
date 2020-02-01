#!/usr/bin/env python


import numpy as np
import json
from spikeforest2_utils import AutoRecordingExtractor, MdaRecordingExtractor
import hither
import kachery as ka
import os

studyset_name = 'PAIRED_ENGLISH'
study_name = 'PAIRED_ENGLISH'
path_from = '/mnt/ceph/users/jjun/groundtruth/paired_english'
path_to = '/mnt/home/jjun/src/spikeforest_recordings/recordings/PAIRED_ENGLISH/paired_english'


def register_recording_test(*, recdir, output_fname, label, to):
    print(f'''
        recdir: {recdir}
        output_fname: {output_fname}
        label: {label}
        to: {to}
    ''')


def register_recording(*, recdir, output_fname, label, to):
    with ka.config(to=to):
        raw_path = ka.store_file(recdir + '/raw.mda')
        obj = dict(
            raw=raw_path,
            params=ka.load_object(recdir + '/params.json'),
            geom=np.genfromtxt(ka.load_file(recdir + '/geom.csv'), delimiter=',').tolist()
        )
        obj['self_reference'] = ka.store_object(obj, basename='{}.json'.format(label))
        with open(output_fname, 'w') as f:
            json.dump(obj, f, indent=4)


def register_groundtruth(*, recdir, output_fname, label, to):
    with ka.config(to=to):
        raw_path = ka.store_file(recdir + '/raw.mda')
        obj = dict(
            firings=raw_path
        )
        obj['self_reference'] = ka.store_object(obj, basename='{}.json'.format(label))
        with open(output_fname, 'w') as f:
            json.dump(obj, f, indent=4)

ka.set_config(
    fr='default_readwrite',
    to='default_readwrite'
)

list_rec = [str(f) for f in os.listdir(path_from) if os.path.isdir(os.path.join(path_from, f))]

print('# files: {}'.format(len(list_rec)))
for rec1 in list_rec:
    print(f'Uploading {rec1}')
    path_rec1 = os.path.join(path_from, rec1)
    if False:
        register_recording(
            recdir = path_rec1, 
            output_fname = os.path.join(path_to, rec1+'.json'),
            label = rec1,
            to = 'default_readwrite'
        )
    if False:
        register_groundtruth(
            recdir = path_rec1, 
            output_fname = os.path.join(path_to, rec1+'.firings_true.json'),
            label = rec1+'.firings_true',
            to = 'default_readwrite'
        )

# write to PAIRED_ENGLISH.json
print(f'STUDYSET: {studyset_name}')
print('STUDY: {}/{}'.format(studyset_name, study_name))
studydir_local = path_to

study['self_reference'] = ka.store_object(study, basename='{}.json'.format(study_name))
with open(os.path.join(path_to, studyset_name + '.json'), 'w') as f:
    json.dump(study, f, indent=4)
