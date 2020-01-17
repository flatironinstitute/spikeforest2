import kachery as ka
from .bandpass_filter import bandpass_filter
import spikeextractors as se
import numpy as np
import hashlib
import json
from .mdaextractors import MdaRecordingExtractor

class AutoRecordingExtractor(se.RecordingExtractor):
    def __init__(self, arg, download=False):
        super().__init__()
        self._hash = None
        if isinstance(arg, str):
            arg = dict(path=arg)
        if isinstance(arg, se.RecordingExtractor):
            self._recording = arg
        else:
            self._recording = None

            # filters
            if ('recording' in arg) and ('filters' in arg):
                recording1 = AutoRecordingExtractor(arg['recording'])
                self._recording = self._apply_filters(recording1, arg['filters'])
                return

            if 'kachery_config' in arg:
                ka.set_config(**arg['kachery_config'])

            if ('raw' in arg) and ('params' in arg) and ('geom' in arg):
                self._recording = MdaRecordingExtractor(timeseries_path=arg['raw'], samplerate=arg['params']['samplerate'], geom=np.array(arg['geom']), download=download)
                return
            else:
                path = arg.get('path', '')
                if not path:
                    path = arg.get('directory', '')
                if path.endswith('.mda'):
                    if 'samplerate' not in arg:
                        raise Exception('Missing argument: samplerate')
                    samplerate = arg['samplerate']
                    self._recording = MdaRecordingExtractor(timeseries_path=path, samplerate=samplerate, download=download)
                    hash0 = _sha1_of_object(dict(
                        timeseries_sha1=ka.get_file_info(path, algorithm='sha1')['sha1'],
                        samplerate=samplerate
                    ))
                    setattr(self, 'hash', hash0)
                elif path.endswith('.nwb.json'):
                    self._recording = NwbJsonRecordingExtractor(file_path=path)
                    hash0 = ka.get_file_info(path)['sha1']
                    setattr(self, 'hash', hash0)
                elif path.endswith('.json') and (not path.endswith('.nwb.json')):
                    obj = ka.load_object(path)
                    if obj is None:
                        raise Exception(f'Unable to load object: {path}')
                    if ('raw' in obj) and ('params' in obj) and ('geom' in obj):
                        self._recording = MdaRecordingExtractor(timeseries_path=obj['raw'], samplerate=obj['params']['samplerate'], geom=np.array(obj['geom']), download=download)
                    else:
                        raise Exception('Problem initializing recording extractor')
                elif ka.get_file_info(path + '/raw.mda'):
                    self._recording = MdaRecordingExtractor(recording_directory=path, download=download)
                else:
                    raise Exception('Unable to initialize recording extractor. Unable to determine format of recording: {}'.format(path))
        self.copy_channel_properties(recording=self._recording)
    
    def _apply_filters(self, recording, filters):
        ret = recording
        for filter0 in filters:
            ret = self._apply_filter(ret, filter0)
        return ret
    
    def _apply_filter(self, recording, filter0):
        if filter0['type'] == 'bandpass_filter':
            args = dict()
            if 'freq_min' in filter0:
                args['freq_min'] = filter0['freq_min']
            if 'freq_max' in filter0:
                args['freq_max'] = filter0['freq_max']
            if 'freq_wid' in filter0:
                args['freq_wid'] = filter0['freq_wid']
            return bandpass_filter(recording, **args)
        return None
    
    def hash(self):
        if not self._hash:
            if hasattr(self._recording, 'hash'):
                if type(self._recording.hash) == str:
                    self._hash = self._recording.hash
                else:
                    self._hash = self._recording.hash()
            else:
                self._hash = _samplehash(self._recording)
        return self._hash

    def get_channel_ids(self):
        return self._recording.get_channel_ids()

    def get_num_frames(self):
        return self._recording.get_num_frames()

    def get_sampling_frequency(self):
        return self._recording.get_sampling_frequency()

    def get_traces(self, channel_ids=None, start_frame=None, end_frame=None):
        return self._recording.get_traces(channel_ids=channel_ids, start_frame=start_frame, end_frame=end_frame)

class NwbJsonRecordingExtractor(se.RecordingExtractor):
    extractor_name = 'NwbJsonRecordingExtractor'
    is_writable = False
    def __init__(self, file_path):
        import h5_to_json as h5j
        se.RecordingExtractor.__init__(self)
        X = ka.load_object(file_path)
        X = h5j.hierarchy(X)
        self._timeseries = h5j.get_value(X['root']['acquisition']['ElectricalSeries']['_datasets']['data'], use_kachery=True, lazy=True)
        self._sampling_frequency = 30000 # hard-coded for now -- TODO: need to get this from the file
        self._geom = None # TODO: need to get this from the file
        if self._geom is not None:
            for m in range(self._timeseries.shape[0]):
                self.set_channel_property(m, 'location', self._geom[m, :])

    def get_channel_ids(self):
        return list(range(self._timeseries.shape[1]))

    def get_num_frames(self):
        return self._timeseries.shape[0]

    def get_sampling_frequency(self):
        return self._sampling_frequency

    def get_traces(self, channel_ids=None, start_frame=None, end_frame=None):
        if start_frame is None:
            start_frame = 0
        if end_frame is None:
            end_frame = self.get_num_frames()
        if channel_ids is None:
            channel_ids = self.get_channel_ids()
        recordings = self._timeseries[start_frame:end_frame, :][:, channel_ids].T
        return recordings

class NwbElectricalSeriesRecordingExtractor(se.RecordingExtractor):
    def __init__(self, *, path, nwb_path):
        import h5py
        super().__init__()
        self._path = path
        self._nwb_path = nwb_path
        with h5py.File(self._path, 'r') as f:
            X = load_nwb_item(file=f, nwb_path=self._nwb_path)
            self._samplerate = X['starting_time'].attrs['rate']
            self._num_timepoints = X['data'].shape[0]
            self._num_channels = X['data'].shape[1]

    def get_channel_ids(self):
        return list(range(self._num_channels))

    def get_num_frames(self):
        return self._num_timepoints

    def get_sampling_frequency(self):
        return self._samplerate

    def get_traces(self, channel_ids=None, start_frame=None, end_frame=None):
        import h5py
        if start_frame is None:
            start_frame = 0
        if end_frame is None:
            end_frame = self.get_num_frames()
        if channel_ids is None:
            channel_ids = self.get_channel_ids()
        with h5py.File(self._path, 'r') as f:
            X = load_nwb_item(file=f, nwb_path=self._nwb_path)
            return X['data'][start_frame:end_frame, :][:, channel_ids].T

def _samplehash(recording):
    obj = {
        'channels': tuple(recording.get_channel_ids()),
        'frames': recording.get_num_frames(),
        'data': _samplehash_helper(recording)
    }
    return _sha1_of_object(obj)


def _samplehash_helper(recording):
    rng = np.random.RandomState(37)
    n_samples = min(recording.get_num_frames() // 1000, 100)
    inds = rng.randint(low=0, high=recording.get_num_frames(), size=n_samples)
    h = 0
    for i in inds:
        t = recording.get_traces(start_frame=i, end_frame=i + 100)
        h = hash((hash(bytes(t)), hash(h)))
    return h

def _sha1_of_string(txt: str) -> str:
    hh = hashlib.sha1(txt.encode('utf-8'))
    ret = hh.hexdigest()
    return ret


def _sha1_of_object(obj: object) -> str:
    txt = json.dumps(obj, sort_keys=True, separators=(',', ':'))
    return _sha1_of_string(txt)
