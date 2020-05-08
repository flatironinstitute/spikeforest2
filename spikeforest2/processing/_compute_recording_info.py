import json
import hither_sf as hither
import numpy as np
import sys
from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor

@hither.function('compute_recording_info', version='0.1.1')
@hither.output_file('json_out')
@hither.container(default='docker://magland/spikeforest2:0.1.1')
@hither.local_module('../../spikeforest2_utils')
def compute_recording_info(recording_path, json_out):
    recording = AutoRecordingExtractor(recording_path)
    obj = dict(
        samplerate=recording.get_sampling_frequency(),
        num_channels=len(recording.get_channel_ids()),
        duration_sec=recording.get_num_frames() / recording.get_sampling_frequency()
    )
    with open(json_out, 'w') as f:
        json.dump(obj, f)