from spikeextractors import RecordingExtractor
from spikeextractors import SortingExtractor

import kachery as ka
import json
import numpy as np
from .mdaio import DiskReadMda, readmda, writemda32, writemda64, writemda, appendmda
import os


class MdaRecordingExtractor(RecordingExtractor):
    def __init__(self, *, recording_directory=None, timeseries_path=None, download=False, samplerate=None, geom=None, geom_path=None, params_path=None):
        RecordingExtractor.__init__(self)
        if recording_directory:
            timeseries_path = recording_directory + '/raw.mda'
            geom_path = recording_directory + '/geom.csv'
            params_path = recording_directory + '/params.json'
        self._timeseries_path = timeseries_path
        if params_path:
            self._dataset_params = ka.load_object(params_path)
            self._samplerate = self._dataset_params['samplerate']
        else:
            self._dataset_params = dict(
                samplerate=samplerate
            )
            self._samplerate = samplerate
            
        if download:
            path0 = ka.load_file(path=self._timeseries_path)
            if not path0:
                raise Exception('Unable to realize file: ' + self._timeseries_path)
            self._timeseries_path = path0

        self._timeseries = DiskReadMda(self._timeseries_path)
        if self._timeseries is None:
            raise Exception('Unable to load timeseries: {}'.format(self._timeseries_path))
        X = self._timeseries
        if geom is not None:
            self._geom = geom
        elif geom_path:
            geom_path2 = ka.load_file(geom_path)
            self._geom = np.genfromtxt(geom_path2, delimiter=',')
        else:
            self._geom = np.zeros((X.N1(), 2))
        
        if self._geom.shape[0] != X.N1():
            # raise Exception(
            #    'Incompatible dimensions between geom.csv and timeseries file {} <> {}'.format(self._geom.shape[0], X.N1()))
            print('WARNING: Incompatible dimensions between geom.csv and timeseries file {} <> {}'.format(self._geom.shape[0], X.N1()))
            self._geom = np.zeros((X.N1(), 2))
        
        self._hash = ka.get_object_hash(dict(
            timeseries=ka.get_file_hash(self._timeseries_path),
            samplerate=self._samplerate,
            geom=_json_serialize(self._geom)
        ))

        self._num_channels = X.N1()
        self._num_timepoints = X.N2()
        for m in range(self._num_channels):
            self.set_channel_property(m, 'location', self._geom[m, :])

    def get_channel_ids(self):
        return list(range(self._num_channels))

    def get_num_frames(self):
        return self._num_timepoints

    def get_sampling_frequency(self):
        return self._samplerate

    def get_traces(self, channel_ids=None, start_frame=None, end_frame=None):
        if start_frame is None:
            start_frame = 0
        if end_frame is None:
            end_frame = self.get_num_frames()
        if channel_ids is None:
            channel_ids = self.get_channel_ids()
        X = self._timeseries
        recordings = X.readChunk(i1=0, i2=start_frame, N1=X.N1(), N2=end_frame - start_frame)
        recordings = recordings[channel_ids, :]
        return recordings
    
    def hash(self):
        return self._hash

    @staticmethod
    def write_recording(recording, save_path, params=dict(), raw_fname='raw.mda', params_fname='params.json', 
            _preserve_dtype=False, in_blocks=False):
        if in_blocks:
            return write_recording_blocks(recording, save_path, params, raw_fname, params_fname, _preserve_dtype)

        channel_ids = recording.get_channel_ids()
        M = len(channel_ids)
        # N = recording.get_num_frames()
        raw = recording.get_traces()
        location0 = recording.get_channel_property(channel_ids[0], 'location')
        nd = len(location0)
        geom = np.zeros((M, nd))
        for ii in range(len(channel_ids)):
            location_ii = recording.get_channel_property(channel_ids[ii], 'location')
            geom[ii, :] = list(location_ii)
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
        if _preserve_dtype:
            writemda(raw, save_path + '/' + raw_fname, dtype=raw.dtype)
        else:
            writemda32(raw, save_path + '/' + raw_fname)
        params["samplerate"] = recording.get_sampling_frequency()
        with open(save_path + '/' + params_fname, 'w') as f:
            json.dump(params, f)
        np.savetxt(save_path + '/geom.csv', geom, delimiter=',')


class MdaSortingExtractor(SortingExtractor):
    def __init__(self, firings_file, samplerate):
        SortingExtractor.__init__(self)
        self._firings_path = ka.load_file(firings_file)
        if not self._firings_path:
            raise Exception('Unable to load firings file: ' + firings_file)

        self._firings = readmda(self._firings_path)
        self._sampling_frequency = samplerate
        self._times = self._firings[1, :]
        self._labels = self._firings[2, :]
        self._unit_ids = np.unique(self._labels).astype(int)

    def get_unit_ids(self):
        return self._unit_ids

    def get_unit_spike_train(self, unit_id, start_frame=None, end_frame=None):
        if start_frame is None:
            start_frame = 0
        if end_frame is None:
            end_frame = np.Inf
        inds = np.where((self._labels == unit_id) & (start_frame <= self._times) & (self._times < end_frame))
        return np.rint(self._times[inds]).astype(int)

    def get_sampling_frequency(self):
        return self._sampling_frequency

    def hash(self):
        return ka.get_object_hash(dict(
            firings=ka.get_file_hash(self._firings_path),
            samplerate=self._sampling_frequency
        ))

    @staticmethod
    def write_sorting(sorting, save_path):
        unit_ids = sorting.get_unit_ids()
        # if len(unit_ids) > 0:
        #     K = np.max(unit_ids)
        # else:
        #     K = 0
        times_list = []
        labels_list = []
        for i in range(len(unit_ids)):
            unit = unit_ids[i]
            times = sorting.get_unit_spike_train(unit_id=unit)
            times_list.append(times)
            labels_list.append(np.ones(times.shape) * unit)
        all_times = _concatenate(times_list)
        all_labels = _concatenate(labels_list)
        sort_inds = np.argsort(all_times)
        all_times = all_times[sort_inds]
        all_labels = all_labels[sort_inds]
        L = len(all_times)
        firings = np.zeros((3, L))
        firings[1, :] = all_times
        firings[2, :] = all_labels
        writemda64(firings, save_path)


def _concatenate(list):
    if len(list) == 0:
        return np.array([])
    return np.concatenate(list)


def is_kbucket_url(path):
    path = path or ''
    return path.startswith('kbucket://') or path.startswith('sha1://') or path.startswith('sha1dir://')


def is_url(path):
    path = path or ''
    return path.startswith('http://') or path.startswith('https://') or path.startswith(
        'kbucket://') or path.startswith('sha1://') or path.startswith('sha1dir://')


def write_recording_blocks(recording, save_path, params=dict(), raw_fname='raw.mda', params_fname='params.json',
        _preserve_dtype=False):
    import math
    if not os.path.isdir(save_path):
        os.mkdir(save_path)

    channel_ids = recording.get_channel_ids()
    M = len(channel_ids)
    N = recording.get_num_frames()

    block_size = 20000 * 60 * 10
    n_blocks = math.ceil((N*1.0) / block_size)

    # open file
    total_size = 0
    for i in range(n_blocks):
        i_start = (i*block_size)
        if i == (n_blocks - 1):
            i_end = N
        else:
            i_end = i_start+block_size
        block = recording.get_traces(start_frame=i_start, end_frame=i_end)
        if i == 0:
            writemda32(block, save_path + '/' + raw_fname)
        else:
            appendmda(block, save_path + '/' + raw_fname)
        # write block
        total_size = total_size + np.shape(block)[1]

    location0 = recording.get_channel_property(channel_ids[0], 'location')
    nd = len(location0)
    geom = np.zeros((M, nd))
    for ii in range(len(channel_ids)):
        location_ii = recording.get_channel_property(channel_ids[ii], 'location')
        geom[ii, :] = list(location_ii)

    params["samplerate"] = recording.get_sampling_frequency()
    with open(save_path + '/' + params_fname,'w') as f:
        json.dump(params, f)
    np.savetxt(save_path + '/geom.csv', geom, delimiter=',')

def _listify_ndarray(x):
    if x.ndim == 1:
        if np.issubdtype(x.dtype, np.integer):
            return [int(val) for val in x]
        else:
            return [float(val) for val in x]
    elif x.ndim == 2:
        ret = []
        for j in range(x.shape[1]):
            ret.append(_listify_ndarray(x[:, j]))
        return ret
    elif x.ndim == 3:
        ret = []
        for j in range(x.shape[2]):
            ret.append(_listify_ndarray(x[:, :, j]))
        return ret
    elif x.ndim == 4:
        ret = []
        for j in range(x.shape[3]):
            ret.append(_listify_ndarray(x[:, :, :, j]))
        return ret
    else:
        raise Exception('Cannot listify ndarray with {} dims.'.format(x.ndim))

def _json_serialize(x):
    if isinstance(x, np.ndarray):
        return _listify_ndarray(x)
    elif isinstance(x, np.integer):
        return int(x)
    elif isinstance(x, np.floating):
        return float(x)
    elif type(x) == dict:
        ret = dict()
        for key, val in x.items():
            ret[key] = _json_serialize(val)
        return ret
    elif type(x) == list:
        ret = []
        for i, val in enumerate(x):
            ret.append(_json_serialize(val))
        return ret
    else:
        return x