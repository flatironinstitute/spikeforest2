from mountaintools import client as mt
from mountaintools import MountainClient
import traceback
import spikeextractors as se
import numpy as np
import io
import base64
import time
from spikeforest2_utils import AutoRecordingExtractor, writemda32
import logging
logger = logging.getLogger('reactopya')

class TimeseriesView:
    def __init__(self):
        super().__init__()
        self._recording = None
        self._multiscale_recordings = None
        self._segment_size_times_num_channels = 1000000
        self._segment_size = None

    def javascript_state_changed(self, prev_state, state):
        self._set_status('running', 'Running TimeseriesView')
        self._create_efficient_access = state.get('create_efficient_access', False)
        if not self._recording:
            self._set_status('running', 'Loading recording')
            recording0 = state.get('recording', None)
            if not recording0:
                self._set_error('Missing: recording')
                return
            try:
                self._recording = AutoRecordingExtractor(recording0)
            except Exception as err:
                traceback.print_exc()
                self._set_error('Problem initiating recording: {}'.format(err))
                return

            self._set_status('running', 'Loading recording data')            
            traces0 = self._recording.get_traces(channel_ids=self._recording.get_channel_ids(), start_frame=0, end_frame=min(self._recording.get_num_frames(), 25000))
            y_offsets = -np.mean(traces0, axis=1)
            for m in range(traces0.shape[0]):
                traces0[m, :] = traces0[m, :] + y_offsets[m]
            vv = np.percentile(np.abs(traces0), 90)
            y_scale_factor = 1 / (2 * vv) if vv > 0 else 1
            self._segment_size = int(np.ceil(self._segment_size_times_num_channels / self._recording.get_num_channels()))
            try:
                channel_locations = self._recording.get_channel_locations()
            except:
                channel_locations = None
            self.set_state(dict(
                num_channels=self._recording.get_num_channels(),
                channel_ids=self._recording.get_channel_ids(),
                channel_locations=channel_locations,
                num_timepoints=self._recording.get_num_frames(),
                y_offsets=y_offsets,
                y_scale_factor=y_scale_factor,
                samplerate=self._recording.get_sampling_frequency(),
                segment_size=self._segment_size,
                status_message='Loaded recording.'
            ))
    
        # SR = state.get('segmentsRequested', {})
        # for key in SR.keys():
        #     aa = SR[key]
        #     if not self.get_python_state(key, None):
        #         self.set_state(dict(status_message='Loading segment {}'.format(key)))
        #         data0 = self._load_data(aa['ds'], aa['ss'])
        #         data0_base64 = _mda32_to_base64(data0)
        #         state0 = {}
        #         state0[key] = dict(data=data0_base64, ds=aa['ds'], ss=aa['ss'])
        #         self.set_state(state0)
        #         self.set_state(dict(status_message='Loaded segment {}'.format(key)))
        self._set_status('finished', '')
    
    def on_message(self, msg):
        
        if msg['command'] == 'requestSegment':
            ds = msg['ds_factor']
            ss = msg['segment_num']
            data0 = self._load_data(ds, ss)
            data0_base64 = _mda32_to_base64(data0)
            self.send_message(dict(
                command='setSegment',
                ds_factor=ds,
                segment_num=ss,
                data=data0_base64
            ))

    def _load_data(self, ds, ss):
        if not self._recording:
            return
        logger.info('_load_data {} {}'.format(ds, ss))
        if ds > 1:
            if self._multiscale_recordings is None:
                self.set_state(dict(status_message='Creating multiscale recordings...'))
                self._multiscale_recordings = _create_multiscale_recordings(
                    recording=self._recording,
                    progressive_ds_factor=3,
                    create_efficient_access=self._create_efficient_access
                )
                self.set_state(dict(status_message='Done creating multiscale recording'))
            rx = self._multiscale_recordings[ds]
            # print('_extract_data_segment', ds, ss, self._segment_size)
            start_time = time.time()
            X = _extract_data_segment(recording=rx, segment_num=ss, segment_size=self._segment_size * 2)
            # print('done extracting data segment', time.time() - start_time)
            logger.info('extracted data segment {} {} {}'.format(ds, ss, time.time() - start_time))
            return X

        start_time = time.time()
        traces = self._recording.get_traces(
            start_frame=ss*self._segment_size, end_frame=(ss+1)*self._segment_size)
        logger.info('extracted data segment {} {} {}'.format(ds, ss, time.time() - start_time))
        return traces

    def iterate(self):
        pass

    def _set_state(self, **kwargs):
        self.set_state(kwargs)
    
    def _set_error(self, error_message):
        self._set_status('error', error_message)
    
    def _set_status(self, status, status_message=''):
        self._set_state(status=status, status_message=status_message)

def _mda32_to_base64(X):
    f = io.BytesIO()
    writemda32(X, f)
    return base64.b64encode(f.getvalue()).decode('utf-8')

def _extract_data_segment(*, recording, segment_num, segment_size):
    segment_num = int(segment_num)
    segment_size = int(segment_size)
    a1 = segment_size * segment_num
    a2 = segment_size * (segment_num + 1)
    if a1 > recording.get_num_frames():
        a1 = recording.get_num_frames()
    if a2 > recording.get_num_frames():
        a2 = recording.get_num_frames()
    X = recording.get_traces(start_frame=a1, end_frame=a2)
    return X

def _create_multiscale_recordings(*, recording, progressive_ds_factor, create_efficient_access=True):
    ret = dict()
    current_rx = recording
    current_ds_factor = 1
    N = recording.get_num_frames()
    recording_has_minmax = False
    while current_ds_factor * progressive_ds_factor < N:
        current_rx = _DownsampledRecordingExtractor(
            recording=current_rx, ds_factor=progressive_ds_factor, input_has_minmax=recording_has_minmax)
        if create_efficient_access:
            current_rx = EfficientAccessRecordingExtractor(recording=current_rx)
        current_ds_factor = current_ds_factor * progressive_ds_factor
        ret[current_ds_factor] = current_rx
        recording_has_minmax = True
    return ret


class _DownsampledRecordingExtractor(se.RecordingExtractor):
    def __init__(self, *, recording, ds_factor, input_has_minmax):
        se.RecordingExtractor.__init__(self)
        self._recording = recording
        self._ds_factor = ds_factor
        self._input_has_minmax = input_has_minmax
        self._recording_hash = None
        self.copy_channel_properties(recording)

    def hash(self):
        if not self._recording_hash:
            if hasattr(self._recording, 'hash'):
                if type(self._recording.hash) == str:
                    self._recording_hash = self._recording.hash
                else:
                    self._recording_hash = self._recording.hash()
            else:
                self._recording_hash = _samplehash(self._recording)
        return mt.sha1OfObject(dict(
            name='downsampled-recording-extractor',
            version=2,
            recording=self._recording_hash,
            ds_factor=self._ds_factor,
            input_has_minmax=self._input_has_minmax
        ))

    def get_channel_ids(self):
        # same channel IDs
        return self._recording.get_channel_ids()

    def get_num_frames(self):
        if self._input_has_minmax:
            # number of frames is just /ds_factor (but not quite -- tricky!)
            return ((self._recording.get_num_frames() // 2) // self._ds_factor) * 2
        else:
            # need to double because we will now keep track of mins and maxs
            return (self._recording.get_num_frames() // self._ds_factor) * 2

    def get_sampling_frequency(self):
        if self._input_has_minmax:
            # sampling frequency is just /ds_factor
            return self._recording.get_sampling_frequency() / self._ds_factor
        else:
            # need to double because we will now keep track of mins and maxes
            return (self._recording.get_sampling_frequency() / self._ds_factor) * 2

    def get_traces(self, channel_ids=None, start_frame=None, end_frame=None):
        ds_factor = self._ds_factor
        if self._input_has_minmax:
            # get the traces *ds_factor
            X = self._recording.get_traces(
                channel_ids=channel_ids,
                start_frame=start_frame * ds_factor,
                end_frame=end_frame * ds_factor
            )
            X_mins = X[:, 0::2]  # here are the minimums
            X_maxs = X[:, 1::2]  # here are the maximums
            X_mins_reshaped = np.reshape(
                X_mins, (X_mins.shape[0], X_mins.shape[1] // ds_factor, ds_factor), order='C')
            X_maxs_reshaped = np.reshape(
                X_maxs, (X_maxs.shape[0], X_maxs.shape[1] // ds_factor, ds_factor), order='C')
            # the size of the output is the size X divided by ds_factor
            ret = np.zeros((X.shape[0], X.shape[1] // ds_factor))
            ret[:, 0::2] = np.min(X_mins_reshaped, axis=2)  # here are the mins
            ret[:, 1::2] = np.max(X_maxs_reshaped, axis=2)  # here are the maxs
            return ret
        else:
            X = self._recording.get_traces(
                channel_ids=channel_ids,
                start_frame=start_frame * self._ds_factor // 2,
                end_frame=end_frame * self._ds_factor // 2
            )
            X_reshaped = np.reshape(
                X, (X.shape[0], X.shape[1] // ds_factor, ds_factor), order='C')
            ret = np.zeros((X.shape[0], (X.shape[1] // ds_factor) * 2))
            ret[:, 0::2] = np.min(X_reshaped, axis=2)
            ret[:, 1::2] = np.max(X_reshaped, axis=2)
            return ret

    @staticmethod
    def write_recording(recording, save_path):
        EfficientAccessRecordingExtractor(
            recording=recording, _dest_path=save_path)

def _samplehash(recording):
    from mountaintools import client as mt
    obj = {
        'channels': tuple(recording.get_channel_ids()),
        'frames': recording.get_num_frames(),
        'data': _samplehash_helper(recording)
    }
    return mt.sha1OfObject(obj)


def _samplehash_helper(recording):
    rng = np.random.RandomState(37)
    n_samples = min(recording.get_num_frames() // 1000, 100)
    inds = rng.randint(low=0, high=recording.get_num_frames(), size=n_samples)
    h = 0
    for i in inds:
        t = recording.get_traces(start_frame=i, end_frame=i + 100)
        h = hash((hash(bytes(t)), hash(h)))
    return h
