#!/usr/bin/env python

import argparse
import json
from spikeforest2_utils.autoextractors.autosortingextractor import AutoSortingExtractor
from spikeforest2_utils.autoextractors.autorecordingextractor import AutoRecordingExtractor
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
    # parser.add_argument('--job_timeout', help='Job timeout in seconds. Default is 20 minutes = 1200 seconds.', required=False, default=1200)
    # parser.add_argument('--slurm', help='Optional SLURM configuration file (.json format)', required=False, default=None)
    # parser.add_argument('--verbose', help='Provide some additional verbose output.', action='store_true')
    parser.add_argument('spec', help='Path to the .json file containing the analysis specification')
    parser.add_argument('--output', '-o', help='The output .json file', required=True)
    parser.add_argument('--force-run', help='Force rerunning of all spike sorting', action='store_true')
    parser.add_argument('--force-run-all', help='Force rerunning of all spike sorting and other processing', action='store_true')
    parser.add_argument('--parallel', help='Optional number of parallel jobs', required=False, default='0')    
    parser.add_argument('--slurm', help='Path to slurm config file', required=False, default=None)
    parser.add_argument('--cache', help='The cache database to use', required=False, default=None)
    parser.add_argument('--test', help='Only run a few.', action='store_true')

    args = parser.parse_args()
    force_run = args.force_run or args.force_run_all
    force_run_all = args.force_run_all

    with open(args.spec, 'r') as f:
        spec = json.load(f)

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
    elif args.slurm:
        with open(args.slurm, 'r') as f:
            slurm_config = json.load(f)
        job_handler = hither.SlurmJobHandler(
            working_dir='tmp_slurm',
            use_slurm=slurm_config['cpu'].get('use_slurm', True),
            num_workers_per_batch=slurm_config['cpu'].get('num_workers_per_batch', 14),
            num_cores_per_job=slurm_config['cpu'].get('num_cores_per_job', 2),
            time_limit_per_batch=slurm_config['cpu'].get('time_limit_per_batch', 3600),
            max_simultaneous_batches=slurm_config['cpu'].get('max_simultaneous_batches', 10),
            additional_srun_opts=slurm_config['cpu'].get('additional_srun_opts', [])
        )
        job_handler_gpu = hither.SlurmJobHandler(
            working_dir='tmp_slurm',
            use_slurm=slurm_config['gpu'].get('use_slurm', True),
            num_workers_per_batch=slurm_config['gpu'].get('num_workers_per_batch', 14),
            num_cores_per_job=slurm_config['gpu'].get('num_cores_per_job', 2),
            time_limit_per_batch=slurm_config['gpu'].get('time_limit_per_batch', 3600),
            max_simultaneous_batches=slurm_config['gpu'].get('max_simultaneous_batches', 10),
            additional_srun_opts=slurm_config['gpu'].get('additional_srun_opts', [])
        )
    else:
        job_handler = None
        job_handler_gpu = None

    with hither.job_queue(), hither.config(
        container='default',
        cache=args.cache,
        force_run=force_run_all,
        job_handler=job_handler
    ):
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
                recording_path = recording['directory']
                sorting_true_path = recording['firingsTrue']

                algorithm = sorter['processor_name']
                if not hasattr(sorters, algorithm):
                    raise Exception(f'No such sorting algorithm: {algorithm}')
                Sorter = getattr(sorters, algorithm)

                gpu = (algorithm in ['kilosort2', 'ironclust'])
                jh = job_handler
                if gpu:
                    jh = job_handler_gpu
                with hither.config(gpu=gpu, force_run=force_run, exception_on_fail=False, job_handler=jh):
                    sorting_result = Sorter.run(
                        _label=f'{algorithm}:{recording["study"]}/{recording["name"]}',
                        recording_path=recording['directory'],
                        sorting_out=hither.File()
                    )
                    recording['results']['sorting-' + sorter['name']] = sorting_result
                recording['results']['comparison-with-truth-' + sorter['name']] = compare_with_truth.run(
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
        recording['summary'] = dict(
            plots=dict(),
            computed_info=ka.load_object(recording['results']['computed-info'].outputs.json_out._path),
            true_units_info=ka.store_file(recording['results']['true-units-info'].outputs.json_out._path)
        )
    sorting_results = []
    for sorter in spike_sorters:
        for recording in recordings:
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
                    timed_out=False
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

@hither.function('compare_with_truth', '0.1.0')
@hither.input_file('sorting_path')
@hither.input_file('sorting_true_path')
@hither.output_file('json_out')
@hither.container(default='docker://magland/spikeforest2:0.1.0')
@hither.local_module('../../spikeforest2_utils')
def compare_with_truth(sorting_path, sorting_true_path, json_out):
    from spikeforest2_utils import SortingComparison
    sorting = AutoSortingExtractor(sorting_path)
    sorting_true = AutoSortingExtractor(sorting_true_path)
    SC = SortingComparison(sorting_true, sorting, delta_tp=30)
    df = _get_comparison_data_frame(comparison=SC)
    obj = df.transpose().to_dict()
    with open(json_out, 'w') as f:
        json.dump(obj, f, indent=4)

def _get_comparison_data_frame(*, comparison):
    import pandas as pd
    SC = comparison

    unit_properties = []  # snr, etc? these would need to be properties in the sortings of the comparison

    # Compute events counts
    sorting1 = SC.getSorting1()
    sorting2 = SC.getSorting2()
    unit1_ids = sorting1.get_unit_ids()
    unit2_ids = sorting2.get_unit_ids()
    # N1 = len(unit1_ids)
    # N2 = len(unit2_ids)
    event_counts1 = dict()
    for _, u1 in enumerate(unit1_ids):
        times1 = sorting1.get_unit_spike_train(unit_id=u1)
        event_counts1[u1] = len(times1)
    event_counts2 = dict()
    for _, u2 in enumerate(unit2_ids):
        times2 = sorting2.get_unit_spike_train(unit_id=u2)
        event_counts2[u2] = len(times2)

    rows = []
    for _, unit1 in enumerate(unit1_ids):
        unit2 = SC.getBestUnitMatch1(unit1)
        if unit2 >= 0:
            num_matches = SC.getMatchingEventCount(unit1, unit2)
            num_false_negatives = event_counts1[unit1] - num_matches
            num_false_positives = event_counts2[unit2] - num_matches
        else:
            num_matches = 0
            num_false_negatives = event_counts1[unit1]
            num_false_positives = 0
        row0 = {
            'unit_id': unit1,
            'accuracy': _safe_frac(num_matches, num_false_positives + num_false_negatives + num_matches),
            'best_unit': unit2,
            'matched_unit': SC.getMappedSorting1().getMappedUnitIds(unit1),
            'num_matches': num_matches,
            'num_false_negatives': num_false_negatives,
            'num_false_positives': num_false_positives,
            'f_n': _safe_frac(num_false_negatives, num_false_negatives + num_matches),
            'f_p': _safe_frac(num_false_positives, num_false_positives + num_matches)
        }
        for prop in unit_properties:
            pname = prop['name']
            row0[pname] = SC.getSorting1().get_unit_property(unit_id=int(unit1), property_name=pname)
        rows.append(row0)

    df = pd.DataFrame(rows)
    fields = ['unit_id']
    fields = fields + ['accuracy', 'best_unit', 'matched_unit', 'num_matches', 'num_false_negatives', 'num_false_positives', 'f_n', 'f_p']
    for prop in unit_properties:
        pname = prop['name']
        fields.append(pname)
    df = df[fields]
    df['accuracy'] = df['accuracy'].map('{:,.4f}'.format)
    # df['Best match'] = df['Accuracy'].map('{:,.2f}'.format)
    df['f_n'] = df['f_n'].map('{:,.4f}'.format)
    df['f_p'] = df['f_p'].map('{:,.4f}'.format)
    return df


def _safe_frac(numer, denom):
    if denom == 0:
        return 0
    return float(numer) / denom

if __name__ == "__main__":
    main()
