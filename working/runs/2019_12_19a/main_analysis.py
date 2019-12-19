#!/usr/bin/env python

import argparse
import json
from spikeforest2_utils import aggregate_sorting_results
import numpy as np
from typing import List, Union, Dict
import kachery as ka
import hither

def main():
    from spikeforest2 import sorters
    from spikeforest2 import processing

    parser = argparse.ArgumentParser(description='Run the SpikeForest2 main analysis')
    # parser.add_argument('analysis_file', help='Path to the analysis specification file (.json format).')
    # parser.add_argument('--config', help='Configuration file', required=True)
    # parser.add_argument('--output', help='Analysis output file (.json format)', required=True)
    # parser.add_argument('--slurm', help='Optional SLURM configuration file (.json format)', required=False, default=None)
    # parser.add_argument('--verbose', help='Provide some additional verbose output.', action='store_true')
    parser.add_argument('spec', help='Path to the .json file containing the analysis specification')
    parser.add_argument('--output', '-o', help='The output .json file', required=True)
    parser.add_argument('--force-run', help='Force rerunning of all spike sorting', action='store_true')
    parser.add_argument('--force-run-all', help='Force rerunning of all spike sorting and other processing', action='store_true')
    parser.add_argument('--parallel', help='Optional number of parallel jobs', required=False, default='0')    
    parser.add_argument('--slurm', help='Path to slurm config file', required=False, default=None)
    parser.add_argument('--cache', help='The cache database to use', required=False, default=None)
    parser.add_argument('--rerun-failing', help='Rerun sorting jobs that previously failed', action='store_true')
    parser.add_argument('--test', help='Only run a few.', action='store_true')
    parser.add_argument('--job-timeout', help='Timeout for sorting jobs', required=False, default=600)
    parser.add_argument('--log-file', help='Log file for analysis progress', required=False, default=None)

    args = parser.parse_args()
    force_run_all = args.force_run_all

    # the following apply to sorting jobs only
    force_run = args.force_run or args.force_run_all
    job_timeout = float(args.job_timeout)
    cache_failing = True
    rerun_failing = args.rerun_failing

    with open(args.spec, 'r') as f:
        spec = json.load(f)

    # clear the log file    
    if args.log_file is not None:
        with open(args.log_file, 'w'):
            pass

    studysets_path = spec['studysets']
    studyset_names = spec['studyset_names']
    spike_sorters = spec['spike_sorters']

    ka.set_config(fr='default_readonly')

    print(f'Loading study sets object from: {studysets_path}')
    studysets_obj = ka.load_object(studysets_path)
    if not studysets_obj:
        raise Exception(f'Unable to load: {studysets_path}')
    
    all_study_sets = studysets_obj['StudySets']
    study_sets = []
    for studyset in all_study_sets:
        if studyset['name'] in studyset_names:
            study_sets.append(studyset)
    
    if int(args.parallel) > 0:
        job_handler = hither.ParallelJobHandler(int(args.parallel))
        job_handler_gpu = job_handler
        job_handler_ks = job_handler
    elif args.slurm:
        with open(args.slurm, 'r') as f:
            slurm_config = json.load(f)
        job_handler = hither.SlurmJobHandler(
            working_dir='tmp_slurm',
            **slurm_config['cpu']
        )
        job_handler_gpu = hither.SlurmJobHandler(
            working_dir='tmp_slurm',
            **slurm_config['gpu']
        )
        job_handler_ks = hither.SlurmJobHandler(
            working_dir='tmp_slurm',
            **slurm_config['ks']
        )
    else:
        job_handler = None
        job_handler_gpu = None
        job_handler_ks = None

    with hither.config(
        container='default',
        cache=args.cache,
        force_run=force_run_all,
        job_handler=job_handler,
        log_path=args.log_file
    ), hither.job_queue():
        studies = []
        recordings = []
        for studyset in study_sets:
            studyset_name = studyset['name']
            print(f'================ STUDY SET: {studyset_name}')
            studies0 = studyset['studies']
            if args.test:
                studies0 = studies0[:1]
                studyset['studies'] = studies0
            for study in studies0:
                study['study_set'] = studyset_name
                study_name = study['name']
                print(f'======== STUDY: {study_name}')
                recordings0 = study['recordings']
                if args.test:
                    recordings0 = recordings0[:2]
                    study['recordings'] = recordings0
                for recording in recordings0:
                    recording['study'] = study_name
                    recording['study_set'] = studyset_name
                    recording['firings_true'] = recording['firingsTrue']
                    recordings.append(recording)
                studies.append(study)

        # Download recordings
        for recording in recordings:
            ka.load_file(recording['directory'] + '/raw.mda')
            ka.load_file(recording['directory'] + '/firings_true.mda')
        
        # Attach results objects
        for recording in recordings:
            recording['results'] = dict()
        
        # Summarize recordings
        for recording in recordings:
            recording_path = recording['directory']
            sorting_true_path = recording['firingsTrue']
            recording['results']['computed-info'] = processing.compute_recording_info.run(
                _label=f'compute-recording-info:{recording["study"]}/{recording["name"]}',
                recording_path=recording_path,
                json_out=hither.File()
            )
            recording['results']['true-units-info'] = processing.compute_units_info.run(
                _label=f'compute-units-info:{recording["study"]}/{recording["name"]}',
                recording_path=recording_path,
                sorting_path=sorting_true_path,
                json_out=hither.File()
            )
        
        # Spike sorting
        for sorter in spike_sorters:
            for recording in recordings:
                if recording['study_set'] in sorter['studysets']:
                    recording_path = recording['directory']
                    sorting_true_path = recording['firingsTrue']

                    algorithm = sorter['processor_name']
                    if not hasattr(sorters, algorithm):
                        raise Exception(f'No such sorting algorithm: {algorithm}')
                    Sorter = getattr(sorters, algorithm)

                    if algorithm in ['ironclust']:
                        gpu = True
                        jh = job_handler_gpu
                    elif algorithm in ['kilosort', 'kilosort2']:
                        gpu = True
                        jh = job_handler_ks
                    else:
                        gpu = False
                        jh = job_handler
                    with hither.config(gpu=gpu, force_run=force_run, exception_on_fail=False, cache_failing=cache_failing, rerun_failing=rerun_failing, job_handler=jh, job_timeout=job_timeout):
                        sorting_result = Sorter.run(
                            _label=f'{algorithm}:{recording["study"]}/{recording["name"]}',
                            recording_path=recording['directory'],
                            sorting_out=hither.File()
                        )
                        recording['results']['sorting-' + sorter['name']] = sorting_result
                    recording['results']['comparison-with-truth-' + sorter['name']] = processing.compare_with_truth.run(
                        _label=f'comparison-with-truth:{algorithm}:{recording["study"]}/{recording["name"]}',
                        sorting_path=sorting_result.outputs.sorting_out,
                        sorting_true_path=sorting_true_path,
                        json_out=hither.File()
                    )
                    recording['results']['units-info-' + sorter['name']] = processing.compute_units_info.run(
                        _label=f'units-info:{algorithm}:{recording["study"]}/{recording["name"]}',
                        recording_path=recording_path,
                        sorting_path=sorting_result.outputs.sorting_out,
                        json_out=hither.File()
                    )

    # Assemble all of the results
    print('')
    print('=======================================================')
    print('Assembling results...')
    for recording in recordings:
        print(f'Recording: {recording["study"]}/{recording["name"]}')
        recording['summary'] = dict(
            plots=dict(),
            computed_info=ka.load_object(recording['results']['computed-info'].outputs.json_out._path),
            true_units_info=ka.store_file(recording['results']['true-units-info'].outputs.json_out._path)
        )
    sorting_results = []
    for sorter in spike_sorters:
        for recording in recordings:
            if recording['study_set'] in sorter['studysets']:
                print(f'Sorting: {sorter["processor_name"]} {recording["study"]}/{recording["name"]}')
                sorting_result = recording['results']['sorting-' + sorter['name']]
                comparison_result = recording['results']['comparison-with-truth-' + sorter['name']]
                units_info_result = recording['results']['units-info-' + sorter['name']]
                sr = dict(
                    recording=recording,
                    sorter=sorter,
                    firings_true=recording['directory'] + '/firings_true.mda',
                    processor_name=sorter['processor_name'],
                    processor_version=sorting_result.version,
                    execution_stats=dict(
                        start_time=sorting_result.runtime_info['start_time'],
                        end_time=sorting_result.runtime_info['end_time'],
                        elapsed_sec=sorting_result.runtime_info['end_time'] - sorting_result.runtime_info['start_time'],
                        retcode=0 if sorting_result.success else -1,
                        timed_out=sorting_result.runtime_info.get('timed_out', False)
                    ),
                    container=sorting_result.container,
                    console_out=ka.store_text(_console_out_to_str(sorting_result.runtime_info['console_out']))
                )
                if sorting_result.success:
                    sr['firings'] = ka.store_file(sorting_result.outputs.sorting_out._path)
                    sr['comparison_with_truth'] = dict(
                        json=ka.store_file(comparison_result.outputs.json_out._path)
                    )
                    sr['sorted_units_info'] = ka.store_file(units_info_result.outputs.json_out._path)
                else:
                    sr['firings'] = None
                    sr['comparison_with_truth'] = None
                    sr['sorted_units_info'] = None
                sorting_results.append(sr)
    
    # Delete results from recordings
    for recording in recordings:
        del recording['results']

    # Aggregate sorting results
    print('')
    print('=======================================================')
    print('Aggregating sorting results...')
    aggregated_sorting_results = aggregate_sorting_results(studies, recordings, sorting_results)

    # Show output summary
    for sr in aggregated_sorting_results['study_sorting_results']:
        study_name = sr['study']
        sorter_name = sr['sorter']
        n1 = np.array(sr['num_matches'])
        n2 = np.array(sr['num_false_positives'])
        n3 = np.array(sr['num_false_negatives'])
        accuracies = n1 / (n1 + n2 + n3)
        avg_accuracy = np.mean(accuracies)
        txt = 'STUDY: {}, SORTER: {}, AVG ACCURACY: {}'.format(study_name, sorter_name, avg_accuracy)
        print(txt)
    
    output_object = dict(
        studies=studies,
        recordings=recordings,
        study_sets=study_sets,
        sorting_results=sorting_results,
        aggregated_sorting_results=ka.store_object(aggregated_sorting_results, basename='aggregated_sorting_results.json')
    )

    print(f'Writing output to {args.output}...')
    with open(args.output, 'w') as f:
        json.dump(output_object, f, indent=4)
    print('Done.')

def _console_out_to_str(console_out):
    txt = ''
    for console_line in console_out['lines']:
        txt = txt + '{} {}: {}\n'.format(console_out.get('label', ''), _fmt_time(console_line['timestamp']), console_line['text'])
    return txt

def _fmt_time(t):
    import datetime
    return datetime.datetime.fromtimestamp(t).isoformat()


if __name__ == "__main__":
    main()
