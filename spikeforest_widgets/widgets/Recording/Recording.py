from spikeforest2_utils import AutoRecordingExtractor

class Recording:
    def __init__(self):
        super().__init__()
        self._recording = None

    def javascript_state_changed(self, prev_state, state):
        self._set_status('running', 'Running Recording')
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
            try:
                channel_locations = self._recording.get_channel_locations()
            except:
                channel_locations = None
            self.set_state(dict(
                num_channels=self._recording.get_num_channels(),
                channel_ids=self._recording.get_channel_ids(),
                channel_locations=channel_locations,
                num_timepoints=self._recording.get_num_frames(),
                samplerate=self._recording.get_sampling_frequency(),
                status_message='Loaded recording.'
            ))
        self._set_status('finished', '')

    def _set_state(self, **kwargs):
        self.set_state(kwargs)
    
    def _set_error(self, error_message):
        self._set_status('error', error_message)
    
    def _set_status(self, status, status_message=''):
        self._set_state(status=status, status_message=status_message)