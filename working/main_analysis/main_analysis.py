#!/usr/bin/env python

import argparse
from spikeforest2_utils.autoextractors.autosortingextractor import AutoSortingExtractor
from spikeforest2_utils.autoextractors.autorecordingextractor import AutoRecordingExtractor
import numpy as np
from typing import List, Optional
import kachery as ka
import hither
from spikeforest2 import sorters
from spikeforest2 import processing

def main():

    parser = argparse.ArgumentParser(description='Run the SpikeForest2 main analysis')
    # parser.add_argument('analysis_file', help='Path to the analysis specification file (.json format).')
    # parser.add_argument('--config', help='Configuration file', required=True)
    # parser.add_argument('--output', help='Analysis output file (.json format)', required=True)
    # parser.add_argument('--job_timeout', help='Job timeout in seconds. Default is 20 minutes = 1200 seconds.', required=False, default=1200)
    # parser.add_argument('--slurm', help='Optional SLURM configuration file (.json format)', required=False, default=None)
    # parser.add_argument('--verbose', help='Provide some additional verbose output.', action='store_true')
    parser.add_argument('--force-run', help='Force rerunning of all processing', action='store_true')
    parser.add_argument('--test', help='Only run a few.', action='store_true')

    args = parser.parse_args()
    print(args)
    force_run = args.force_run

    studyset_names = ['SYNTH_MEAREC_TETRODE']
    spike_sorters = [
        dict(
            name='MountainSort4',
            processor_name='mountainsort4',
            sorting_params = dict()
        )
    ]
    spike_sorters = []

    ka.set_config(fr='default_readonly')

    studysets_path = 'sha1://3dff25a16ea0797776a824446a446d7ccf427915/studysets.json'
    print(f'Loading study sets object from: {studysets_path}')
    studysets_obj = ka.load_object(studysets_path)
    if not studysets_obj:
        raise Exception(f'Unable to load: {studysets_path}')

    
    with hither.config(container='default', cache='local', force_run=force_run):
        studysets = studysets_obj['StudySets']
        all_recordings = []
        for studyset in studysets:
            if studyset['name'] in studyset_names:
                studyset_name = studyset['name']
                print(f'================ STUDY SET: {studyset_name}')
                studies = studyset['studies']
                if args.test:
                    studies = studies[:1]
                for study in studies:
                    study_name = study['name']
                    print(f'======== STUDY: {study_name}')
                    recordings = study['recordings']
                    if args.test:
                        recordings = recordings[:1]
                    for recording in recordings:
                        all_recordings.append(recording)

        # Download recordings
        for recording in all_recordings:
            ka.load_file(recording['directory'] + '/raw.mda')
            ka.load_file(recording['directory'] + '/firings_true.mda')
        
        # Summarize recordings
        for recording in all_recordings:
            _summarize_recording(recording=recording, args=args)
        
        # Spike sorting
        sorting_results = []
        for sorter in spike_sorters:
            for recording in all_recordings:
                algorithm = sorter['processor_name']
                if not hasattr(sorters, algorithm):
                    raise Exception(f'No such sorting algorithm: {algorithm}')
                Sorter = getattr(sorters, algorithm)

                gpu = (algorithm in ['kilosort2', 'ironclust'])
                with hither.config(gpu=gpu):
                    sorting_result = Sorter.run(recording_path=recording['directory'], sorting_out=hither.File())
                sr = dict(
                    recording=recording,
                    sorter=sorter,
                    firings_true=recording['directory'] + '/firings_true.mda',
                    processor_name=sorter['processor_name'],
                    processor_version=sorting_result.version,
                    execution_stats=sorting_result.runtime_info,
                    stdout=ka.store_text(sorting_result.runtime_info['stdout']),
                    stderr=ka.store_text(sorting_result.runtime_info['stderr']),
                    container=''
                )
                sorting_results.append(sr)

def _summarize_recording(recording, *, args):
    recording_path = recording['directory']
    true_sorting_path = recording['firingsTrue']
    recording['summary'] = dict(
        computed_info=processing.compute_recording_info.run(recording_path=recording_path).retval,
        true_units_info=processing.compute_units_info.run(recording_path=recording_path, sorting_path=true_sorting_path).retval
    ) 

def _sort_study(study, *, args):
    for recording in study['recordings']:
        _sort_recording(recording, args=args)
        if args.test:
            break

def _sort_recording(recording, *, args):
    recording_path = recording['directory']
    sorting_path = sorters.sort(algorithm='mountainsort4', recording_path=recording_path)
    print(sorting_path)

if __name__ == "__main__":
    main()
