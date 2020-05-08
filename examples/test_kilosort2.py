#!/usr/bin/env python

from spikeforest2 import sorters
import hither_sf as hither
import kachery as ka

# recording_path = 'sha1://961f4a641af64dded4821610189f808f0192de4d/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.json'
recording_path = 'sha1://384917d378f85682226a27a32288230fb5ce7e6a/PAIRED_MEA64C_YGER/paired_mea64c/20170629_patch2.json'

with ka.config(fr='default_readonly'):
    #with hither.config(cache='default_readwrite'):
        with hither.config(container='default', gpu=True):
            result = sorters.kilosort2.run(
                recording_path=recording_path,
                sorting_out=hither.File()
            )

print(result.outputs.sorting_out)
