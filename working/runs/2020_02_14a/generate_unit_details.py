#!/usr/bin/env python

import argparse
import hither
import os
import json
import random
import numpy as np
import kachery as ka

def main():
    from mountaintools import client as mt

    parser = argparse.ArgumentParser(description='Generate unit detail data (including spikesprays) for website')
    parser.add_argument('analysis_path', help='assembled analysis file (output.json)')
    parser.add_argument('--studysets', help='Comma-separated list of study set names to include', required=False, default=None)
    parser.add_argument('--force-run', help='Force rerunning of processing', action='store_true')
    parser.add_argument('--force-run-all', help='Force rerunning of processing including filtering', action='store_true')
    parser.add_argument('--parallel', help='Optional number of parallel jobs', required=False, default='0')    
    parser.add_argument('--slurm', help='Path to slurm config file', required=False, default=None)
    parser.add_argument('--cache', help='The cache database to use', required=False, default=None)
    parser.add_argument('--job-timeout', help='Timeout for processing jobs', required=False, default=600)
    parser.add_argument('--log-file', help='Log file for analysis progress', required=False, default=None)
    parser.add_argument('--force-regenerate', help='Whether to force regenerating spike sprays (for when code has changed)', action='store_true')
    parser.add_argument('--test', help='Whether to just test by running only 1', action='store_true')

    args = parser.parse_args()

    mt.configDownloadFrom(['spikeforest.kbucket'])

    with open(args.analysis_path, 'r') as f:
        analysis = json.load(f)

    if args.studysets is not None:
        studyset_names = args.studysets.split(',')
        print('Using study sets: ', studyset_names)
    else:
        studyset_names = None
    
    study_sets = analysis['StudySets']
    sorting_results = analysis['SortingResults']

    studies_to_include = []
    for ss in study_sets:
        if (studyset_names is None) or (ss['name'] in studyset_names):
            for study in ss['studies']:
                studies_to_include.append(study['name'])
    
    print('Including studies:', studies_to_include)

    print('Determining sorting results to process ({} total)...'.format(len(sorting_results)))
    sorting_results_to_process = []
    sorting_results_to_consider = []
    for sr in sorting_results:
        study_name = sr['studyName']
        if study_name in studies_to_include:
            if 'firings' in sr:
                if sr.get('comparisonWithTruth', None) is not None:
                    sorting_results_to_consider.append(sr)
                    key = dict(
                        name='unit-details-v0.1.0',
                        recording_directory=sr['recordingDirectory'],
                        firings_true=sr['firingsTrue'],
                        firings=sr['firings']
                    )
                    val = mt.getValue(key=key, collection='spikeforest')
                    if (not val) or (args.force_regenerate):
                        sr['key'] = key
                        sorting_results_to_process.append(sr)
    if args.test and len(sorting_results_to_process) > 0:
        sorting_results_to_process = [sorting_results_to_process[0]]
    
    print('Need to process {} of {} sorting results'.format(len(sorting_results_to_process), len(sorting_results_to_consider)))

    recording_directories_to_process = sorted(list(set([sr['recordingDirectory'] for sr in sorting_results_to_process])))
    print('{} recording directories to process'.format(len(recording_directories_to_process)))

    if int(args.parallel) > 0:
        job_handler = hither.ParallelJobHandler(int(args.parallel))
    elif args.slurm:
        with open(args.slurm, 'r') as f:
            slurm_config = json.load(f)
        job_handler = hither.SlurmJobHandler(
            working_dir='tmp_slurm',
            **slurm_config['cpu']
        )
    else:
        job_handler = None

    print('Filtering recordings...')
    filter_results = []
    with hither.config(
        container='default',
        cache=args.cache,
        force_run=args.force_run_all,
        job_handler=job_handler,
        log_path=args.log_file,
        exception_on_fail=True,
        cache_failing=False,
        rerun_failing=True,
        job_timeout=args.job_timeout
    ), hither.job_queue():
        for recdir in recording_directories_to_process:
            result = filter_recording.run(recording_directory=recdir, timeseries_out=hither.File())
            filter_results.append(result)
    filtered_timeseries_by_recdir = dict()
    for i, recdir in enumerate(recording_directories_to_process):
        result0 = filter_results[i]
        if not result0.success:
            raise Exception('Problem computing filtered timeseries for recording: {}'.format(recdir))
        filtered_timeseries_by_recdir[recdir] = result0.outputs.timeseries_out._path
    
    print('Creating spike sprays...')
    with hither.config(
        container='default',
        cache=args.cache,
        force_run=args.force_run or args.force_run_all,
        job_handler=job_handler,
        log_path=args.log_file,
        exception_on_fail=True,
        cache_failing=False,
        rerun_failing=True,
        job_timeout=args.job_timeout
    ), hither.job_queue():
        for sr in sorting_results_to_process:
            recdir = sr['recordingDirectory']
            study_name = sr['studyName']
            rec_name = sr['recordingName']
            sorter_name = sr['sorterName']

            print('====== COMPUTING {}/{}/{}'.format(study_name, rec_name, sorter_name))

            cwt = ka.load_object(path=sr['comparisonWithTruth']['json'])

            filtered_timeseries = filtered_timeseries_by_recdir[recdir]

            spike_spray_results = []
            list0 = list(cwt.values())
            for _, unit in enumerate(list0):
                result = create_spike_sprays.run(
                    recording_directory=recdir,
                    filtered_timeseries=filtered_timeseries,
                    firings_true=os.path.join(recdir, 'firings_true.mda'),
                    firings_sorted=sr['firings'],
                    unit_id_true=unit['unit_id'],
                    unit_id_sorted=unit['best_unit'],
                    json_out=hither.File()
                )
                setattr(result, 'unit', unit)
                spike_spray_results.append(result)
            sr['spike_spray_results'] = spike_spray_results

    for sr in sorting_results_to_process:
        recdir = sr['recordingDirectory']
        study_name = sr['studyName']
        rec_name = sr['recordingName']
        sorter_name = sr['sorterName']

        print('====== SAVING {}/{}/{}'.format(study_name, rec_name, sorter_name))
        spike_spray_results = sr['spike_spray_results']
        key = sr['key']

        unit_details = []
        ok = True
        for i, result in enumerate(spike_spray_results):
            if not result.success:
                print('WARNING: Error creating spike sprays for {}/{}/{}'.format(study_name, rec_name, sorter_name))
                ok = False
                break
            ssobj = ka.load_object(result.outputs.json_out._path)
            if ssobj is None:
                raise Exception('Problem loading spikespray object output.')
            address = mt.saveObject(object=ssobj, upload_to='spikeforest.kbucket')
            unit = getattr(result, 'unit')
            unit_details.append(dict(
                studyName=study_name,
                recordingName=rec_name,
                sorterName=sorter_name,
                trueUnitId=unit['unit_id'],
                sortedUnitId=unit['best_unit'],
                spikeSprayUrl=mt.findFile(path=address, remote_only=True, download_from='spikeforest.kbucket')
            ))

        if ok:
            mt.saveObject(collection='spikeforest', key=key, object=unit_details, upload_to='spikeforest.public')


@hither.function(name='filter_recording', version='0.1.0')
@hither.output_file('timeseries_out') # timeseries out
@hither.container(default='docker://magland/spikeforest2:0.1.1')
@hither.local_module('../../../spikeforest2_utils')
def filter_recording(recording_directory, timeseries_out):
    from spikeforest2_utils import AutoRecordingExtractor
    from spikeforest2_utils import writemda32
    import spiketoolkit as st
    rx = AutoRecordingExtractor(recording_directory)
    rx2 = st.preprocessing.bandpass_filter(recording=rx, freq_min=300, freq_max=6000, freq_wid=1000)
    if not writemda32(rx2.get_traces(), timeseries_out):
        raise Exception('Unable to write output file.')


def _get_random_spike_waveforms(*, recording, sorting, unit, max_num=50, channels=None, snippet_len=100):
    st = sorting.get_unit_spike_train(unit_id=unit)
    num_events = len(st)
    if num_events > max_num:
        event_indices = np.random.choice(
            range(num_events), size=max_num, replace=False)
    else:
        event_indices = range(num_events)

    spikes = recording.get_snippets(reference_frames=st[event_indices].astype(int), snippet_len=snippet_len,
                                    channel_ids=channels)
    if len(spikes) > 0:
        spikes = np.dstack(tuple(spikes))
    else:
        spikes = np.zeros((recording.get_num_channels(), snippet_len, 0))
    return spikes


def get_channels_in_neighborhood(rx, *, central_channel, max_size):
    geom = [rx.get_channel_property(channel_id=ch, property_name='location') for ch in rx.get_channel_ids()]
    loc_central = rx.get_channel_property(channel_id=central_channel, property_name='location')
    dists = [np.sqrt(np.sum((np.array(loc_central) - np.array(loc))**2)) for loc in geom]
    inds = np.argsort(dists)
    if len(inds) > max_size:
        inds = inds[0:max_size]
    chan_ids = rx.get_channel_ids()
    ret = [chan_ids[ind] for ind in inds]
    return ret


def get_unmatched_times(times1, times2, *, delta):
    times1 = np.array(times1)
    times2 = np.array(times2)
    times_concat = np.concatenate((times1, times2))
    membership = np.concatenate(
        (np.ones(times1.shape) * 1, np.ones(times2.shape) * 2))
    indices = times_concat.argsort()
    times_concat_sorted = times_concat[indices]
    membership_sorted = membership[indices]
    diffs = times_concat_sorted[1:] - times_concat_sorted[:-1]
    unmatched_inds = 1 + np.where((diffs[1:] > delta) & (diffs[:-1] > delta) & (membership_sorted[1:-1] == 1))[0]
    if (diffs[0] > delta) and (membership_sorted[0] == 1):
        unmatched_inds = np.concatenate(([0], unmatched_inds))
    if (diffs[-1] > delta) and (membership_sorted[-1] == 1):
        unmatched_inds = np.concatenate(
            (unmatched_inds, [len(membership_sorted) - 1]))
    return times_concat_sorted[unmatched_inds]


def get_unmatched_sorting(sx1, sx2, ids1, ids2):
    import spikeextractors as se
    ret = se.NumpySortingExtractor()
    for ii in range(len(ids1)):
        id1 = ids1[ii]
        id2 = ids2[ii]
        train1 = sx1.get_unit_spike_train(unit_id=id1)
        train2 = sx2.get_unit_spike_train(unit_id=id2)
        train = get_unmatched_times(train1, train2, delta=100)
        ret.add_unit(id1, train)
    return ret


def create_spikespray_object(waveforms, name, channel_ids):
    return dict(
        name=name,
        num_channels=waveforms.shape[0],
        num_timepoints=waveforms.shape[1],
        num_spikes=waveforms.shape[2],
        channel_ids=channel_ids,
        spike_waveforms=[
            dict(
                channels=[
                    dict(
                        channel_id=ch,
                        waveform=waveforms[ii, :, spike_index].tolist()
                    )
                    for ii, ch in enumerate(channel_ids)
                ]
            )
            for spike_index in range(waveforms.shape[2])
        ]
    )


def _create_spikesprays(*, rx, sx_true, sx_sorted, neighborhood_size, num_spikes, unit_id_true, unit_id_sorted):
    sx_unmatched_true = get_unmatched_sorting(sx_true, sx_sorted, [unit_id_true], [unit_id_sorted])
    sx_unmatched_sorted = get_unmatched_sorting(sx_sorted, sx_true, [unit_id_sorted], [unit_id_true])
    waveforms0 = _get_random_spike_waveforms(recording=rx, sorting=sx_true, unit=unit_id_true)
    avg = np.mean(waveforms0, axis=2)
    peak_chan = np.argmax(np.max(np.abs(avg), axis=1), axis=0)
    nbhd_channels = get_channels_in_neighborhood(rx, central_channel=peak_chan, max_size=7)
    waveforms1 = _get_random_spike_waveforms(recording=rx, sorting=sx_true, unit=unit_id_true, channels=nbhd_channels)
    if unit_id_sorted in sx_sorted.get_unit_ids():
        waveforms2 = _get_random_spike_waveforms(recording=rx, sorting=sx_sorted, unit=unit_id_sorted, channels=nbhd_channels)
    else:
        waveforms2 = np.zeros((waveforms1.shape[0], waveforms1.shape[1], 0))
    if unit_id_true in sx_unmatched_true.get_unit_ids():
        waveforms3 = _get_random_spike_waveforms(recording=rx, sorting=sx_unmatched_true, unit=unit_id_true, channels=nbhd_channels)
    else:
        waveforms3 = np.zeros((waveforms1.shape[0], waveforms1.shape[1], 0))
    if unit_id_sorted in sx_unmatched_sorted.get_unit_ids():
        waveforms4 = _get_random_spike_waveforms(recording=rx, sorting=sx_unmatched_sorted, unit=unit_id_sorted, channels=nbhd_channels)
    else:
        waveforms4 = np.zeros((waveforms1.shape[0], waveforms1.shape[1], 0))

    ret = []
    ret.append(create_spikespray_object(waveforms1, 'true', nbhd_channels))
    ret.append(create_spikespray_object(waveforms2, 'sorted', nbhd_channels))
    ret.append(create_spikespray_object(waveforms3, 'true_missed', nbhd_channels))
    ret.append(create_spikespray_object(waveforms4, 'sorted_false', nbhd_channels))
    return ret


@hither.function(name='create_spike_sprays', version='0.1.1')
@hither.input_file('filtered_timeseries')
@hither.input_file('firings_true')
@hither.input_file('firings_sorted')
@hither.output_file('json_out')
@hither.container(default='docker://magland/spikeforest2:0.1.1')
@hither.local_module('../../../spikeforest2_utils')
def create_spike_sprays(
    recording_directory, # Recording directory
    filtered_timeseries, # filtered timeseries file (.mda)
    firings_true, # True firings (firings_true.mda)
    firings_sorted, # Sorted firings (firings.mda)
    json_out, # Output json object
    unit_id_true, # ID of the true unit
    unit_id_sorted, # ID of the sorted unit
    neighborhood_size=7, # Max size of the electrode neighborhood
    num_spikes=20, # Max number of spikes in the spike spray
):
    from spikeforest2_utils import MdaRecordingExtractor, MdaSortingExtractor
    rx = MdaRecordingExtractor(recording_directory=recording_directory, download=True, timeseries_path=filtered_timeseries)
    sx_true = MdaSortingExtractor(firings_file=firings_true, samplerate=rx.get_sampling_frequency())
    sx = MdaSortingExtractor(firings_file=firings_sorted, samplerate=rx.get_sampling_frequency())
    ssobj = _create_spikesprays(rx=rx, sx_true=sx_true, sx_sorted=sx, neighborhood_size=neighborhood_size, num_spikes=num_spikes, unit_id_true=unit_id_true, unit_id_sorted=unit_id_sorted)
    with open(json_out, 'w') as f:
        json.dump(ssobj, f)


def _random_string(num_chars):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))


if __name__ == "__main__":
    main()
