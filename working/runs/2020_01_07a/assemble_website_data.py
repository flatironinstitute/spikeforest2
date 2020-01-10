#!/usr/bin/env python

import json
import argparse
import os
import frontmatter
from datetime import datetime
import pkg_resources
import kachery as ka

help_txt='Assemble data for SpikeForest website'


def main():
    parser = argparse.ArgumentParser(description=help_txt, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('analysis_files', nargs='+', help='The files generated by the main spikeforest analysis')
    parser.add_argument('--output', '-o', help='The output .json file', required=True)

    args = parser.parse_args()

    ka.set_config(fr='default_readonly')

    print('******************************** LOADING ANALYSIS OUTPUT OBJECTS...')
    studies = []
    study_sets = []
    recordings = []
    sorting_results = []
    studies_included = dict()
    studysets_included = dict()
    recordings_included = dict()
    for analysis_file in args.analysis_files:
        print('Loading: {}'.format(analysis_file))
        obj = ka.load_object(analysis_file)
        if obj is not None:
            for study in obj['studies']:
                if study['name'] not in studies_included:
                    studies.append(study)
                    studies_included[study['name']] = True
            for study_set in obj['study_sets']:
                if study_set['name'] not in studysets_included:
                    study_sets.append(study_set)
                    studysets_included[study_set['name']] = True
            for recording in obj['recordings']:
                label = recording['study'] + '/' + recording['name']
                if label not in recordings_included:
                    recordings.append(recording)
                    recordings_included[label] = True
            sorting_results = sorting_results + obj['sorting_results']
        else:
            raise Exception('Unable to load: {}'.format(analysis_file))

    # ALGORITHMS
    print('******************************** ASSEMBLING ALGORITHMS...')
    algorithms_by_processor_name = dict()
    Algorithms = []
    basepath = '../../../spikeforest2/sorters/descriptions'
    repo_base_url = 'https://github.com/flatironinstitute/spikeforest/blob/master'
    for item in os.listdir(basepath):
        if item.endswith('.md'):
            alg = frontmatter.load(basepath + '/' + item).to_dict()
            alg['markdown_link'] = repo_base_url + '/spikeforest/spikeforestsorters/descriptions/' + item
            alg['markdown'] = alg['content']
            del alg['content']
            if 'processor_name' in alg:
                algorithms_by_processor_name[alg['processor_name']] = alg
            Algorithms.append(alg)
    print([alg['label'] for alg in Algorithms])

    Studies = []
    for study in studies:
        Studies.append(dict(
            name=study['name'],
            studySet=study['study_set'],
            description=study.get('description', ''),
            recordings=[]
            # the following can be obtained from the other collections
            # numRecordings, sorters, etc...
        ))
    print([S['name'] for S in Studies])

    print('******************************** ASSEMBLING STUDY SETS...')
    study_sets_by_name = dict()
    for study_set in study_sets:
        study_sets_by_name[study_set['name']] = study_set
        study_set['studies'] = []
    studies_by_name = dict()
    for study in studies:
        study0 = dict(
            name=study['name'],
            studySetName=study['study_set'],
            recordings=[]
        )
        study_sets_by_name[study['study_set']]['studies'].append(study0)
        studies_by_name[study0['name']] = study0
    for recording in recordings:
        true_units_info = ka.load_object(recording['summary']['true_units_info'])
        if not true_units_info:
            print(recording['summary']['true_units_info'])
            raise Exception('Unable to load true_units_info for recording {}'.format(recording['name']))
        recording0 = dict(
            name=recording['name'],
            studyName=recording['study'],
            studySetName=studies_by_name[recording['study']]['studySetName'],
            directory=recording['directory'],
            firingsTrue=recording['firings_true'],
            sampleRateHz=recording['summary']['computed_info']['samplerate'],
            numChannels=recording['summary']['computed_info']['num_channels'],
            durationSec=recording['summary']['computed_info']['duration_sec'],
            numTrueUnits=len(true_units_info),
            spikeSign=-1  # TODO: set this properly
        )
        studies_by_name[recording0['studyName']]['recordings'].append(recording0)
    StudySets = []
    for study_set in study_sets:
        StudySets.append(study_set)

    # SORTING RESULTS
    print('******************************** SORTING RESULTS...')
    SortingResults = []
    for sr in sorting_results:
        SR = dict(
            recordingName=sr['recording']['name'],
            studyName=sr['recording']['study'],
            sorterName=sr['sorter']['name'],
            processorName=sr['processor_name'],
            processorVersion=sr['processor_version'],
            sortingParameters=sr['sorting_parameters'],
            recordingDirectory=sr['recording']['directory'],
            firingsTrue=sr['recording']['firings_true'],
            consoleOut=sr['console_out'],
            container=sr['container'],
            cpuTimeSec=sr['execution_stats'].get('elapsed_sec', None),
            returnCode=sr['execution_stats'].get('retcode', 0),  # TODO: in future, the default should not be 0 -- rather it should be a required field of execution_stats
            timedOut=sr['execution_stats'].get('timed_out', False),
            startTime=datetime.fromtimestamp(sr['execution_stats'].get('start_time')).isoformat(),
            endTime=datetime.fromtimestamp(sr['execution_stats'].get('end_time')).isoformat()
        )
        if sr.get('firings', None):
            SR['firings'] = sr['firings']
            if sr.get('comparison_with_truth', None):
                SR['comparisonWithTruth'] = sr['comparison_with_truth']
            else:
                print('Warning: comparison with truth not found for sorting result: {} {}/{}'.format(sr['sorter']['name'], sr['recording']['study'], sr['recording']['name']))
                print('Console output is here: ' + sr['console_out'])
        else:
            print('Warning: firings not found for sorting result: {} {}/{}'.format(sr['sorter']['name'], sr['recording']['study'], sr['recording']['name']))
            print('Console output is here: ' + sr['console_out'])
        SortingResults.append(SR)
    # print('Num unit results:', len(UnitResults))

    # SORTERS
    print('******************************** ASSEMBLING SORTERS...')
    sorters_by_name = dict()
    for sr in sorting_results:
        sorters_by_name[sr['sorter']['name']] = sr['sorter']
    Sorters = []
    sorter_names = sorted(list(sorters_by_name.keys()))
    sorter_names = [sorter_name for sorter_name in sorter_names]
    for sorter_name in sorter_names:
        sorter = sorters_by_name[sorter_name]
        alg = algorithms_by_processor_name.get(sorter['processor_name'], dict())
        alg_label = alg.get('label', sorter['processor_name'])
        Sorters.append(dict(
            name=sorter['name'],
            algorithmName=alg_label,
            processorName=sorter['processor_name'],
            processorVersion='0',  # jfm to provide this
            sortingParameters=sorter['params']
        ))
    print([S['name'] + ':' + S['algorithmName'] for S in Sorters])

    # STUDY ANALYSIS RESULTS
    print('******************************** ASSEMBLING STUDY ANALYSIS RESULTS...')
    StudyAnalysisResults = [
        _assemble_study_analysis_result(
            study_name=study['name'],
            study_set_name=study['study_set'],
            recordings=recordings,
            sorting_results=sorting_results,
            sorter_names=sorter_names
        )
        for study in studies
    ]

    # GENERAL
    print('******************************** ASSEMBLING GENERAL INFO...')
    General = [dict(
        dateUpdated=datetime.now().isoformat(),
        packageVersions=dict(
            spikeforest2=pkg_resources.get_distribution("spikeforest2").version
        )
    )]

    obj = dict(
        mode='spike-front',
        StudySets=StudySets,
        SortingResults=SortingResults,
        Sorters=Sorters,
        Algorithms=Algorithms,
        StudyAnalysisResults=StudyAnalysisResults,
        General=General
    )
    print(f'Writing to {args.output}...')
    with open(args.output, 'w') as f:
        json.dump(obj, f, indent=4)
    print('Done.')


def _assemble_study_analysis_result(*, study_name, study_set_name, recordings, sorting_results, sorter_names):
    print('Assembling {} {}'.format(study_set_name, study_name))
    true_units = dict()
    recording_names = []
    irec = 0
    for rec in recordings:
        if rec['study'] == study_name:
            recording_names.append(rec['name'])
            true_units_info = ka.load_object(rec['summary']['true_units_info'])
            for unit_info in true_units_info:
                id0 = unit_info['unit_id']
                true_units[study_name + '/' + rec['name'] + '/{}'.format(id0)] = dict(
                    unit_id=id0,
                    recording_index=irec,
                    snr=unit_info['snr'],
                    firing_rate=unit_info['firing_rate'],
                    num_events=unit_info['num_events'],
                    sorting_results=dict()
                )
            irec = irec + 1
    cpu_times_by_sorter = dict()
    for sorter_name in sorter_names:
        cpu_times_by_sorter[sorter_name] = []
    for sr in sorting_results:
        rec = sr['recording']
        if rec['study'] == study_name:
            sorter_name = sr['sorter']['name']
            if sorter_name in sorter_names:
                if sr.get('comparison_with_truth', None):
                    comparison_with_truth = ka.load_object(sr['comparison_with_truth']['json'])
                    if comparison_with_truth is None:
                        print(sr)
                        raise Exception('Unable to retrieve comparison with truth object for sorting result.')
                    for unit_result in comparison_with_truth.values():
                        id0 = unit_result['unit_id']
                        n_match = unit_result['num_matches']
                        n_fp = unit_result['num_false_positives']
                        n_fn = unit_result['num_false_negatives']
                        accuracy = n_match / (n_match + n_fp + n_fn)
                        if n_match + n_fp > 0:
                            precision = n_match / (n_match + n_fp)
                        else:
                            precision = 0
                        recall = n_match / (n_match + n_fn)
                        true_units[study_name + '/' + rec['name'] + '/{}'.format(id0)]['sorting_results'][sorter_name] = dict(
                            accuracy=accuracy,
                            precision=precision,
                            recall=recall,
                            numMatches=n_match,
                            numFalsePositives=n_fp,
                            numFalseNegatives=n_fn
                        )
                    cpu_times_by_sorter[sorter_name].append(sr['execution_stats'].get('elapsed_sec', None))
                else:
                    cpu_times_by_sorter[sorter_name].append(None)

    keys0 = sorted(true_units.keys())
    true_units_list = [true_units[key] for key in keys0]

    snrs = [_round(x['snr'], 3) for x in true_units_list]
    firing_rates = [_round(x['firing_rate'], 3) for x in true_units_list]
    num_events = [x['num_events'] for x in true_units_list]
    recording_indices = [x['recording_index'] for x in true_units_list]
    unit_ids = [x['unit_id'] for x in true_units_list]

    study_analysis_result = dict(
        studyName=study_name,
        studySetName=study_set_name,
        recordingNames=recording_names,
        trueSnrs=snrs,
        trueFiringRates=firing_rates,
        trueNumEvents=num_events,
        trueRecordingIndices=recording_indices,
        trueUnitIds=unit_ids,
        sortingResults=[]
    )
    for sorter_name in sorter_names:
        accuracies = [_round(x['sorting_results'].get(sorter_name, {}).get('accuracy'), 3) for x in true_units_list]
        precisions = [_round(x['sorting_results'].get(sorter_name, {}).get('precision'), 3) for x in true_units_list]
        recalls = [_round(x['sorting_results'].get(sorter_name, {}).get('recall'), 3) for x in true_units_list]
        numMatches = [_round(x['sorting_results'].get(sorter_name, {}).get('numMatches'), 3) for x in true_units_list]
        numFalsePositives = [_round(x['sorting_results'].get(sorter_name, {}).get('numFalsePositives'), 3) for x in true_units_list]
        numFalseNegatives = [_round(x['sorting_results'].get(sorter_name, {}).get('numFalseNegatives'), 3) for x in true_units_list]
        study_analysis_result['sortingResults'].append(dict(
            sorterName=sorter_name,
            accuracies=accuracies,
            precisions=precisions,
            numMatches=numMatches,
            numFalsePositives=numFalsePositives,
            numFalseNegatives=numFalseNegatives,
            recalls=recalls,
            cpuTimesSec=cpu_times_by_sorter[sorter_name]
        ))
    # print(study_analysis_result['studyName'], study_analysis_result['sortingResults'][0]['cpuTimesSec'])

    return study_analysis_result


def _round(x, num):
    if x is None:
        return None
    return round(x, num)

if __name__ == "__main__":
    main()
