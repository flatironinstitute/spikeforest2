#!/usr/bin/env python

from spikeforest2 import sorters
import hither_sf as hither
import kachery as ka

recording_path = 'sha1://961f4a641af64dded4821610189f808f0192de4d/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.json'

with ka.config(fr='default_readonly'):
    #with hither.config(cache='default_readwrite'):
        with hither.config(container='default'):
            result = sorters.herdingspikes2.run(
                recording_path=recording_path,
                sorting_out=hither.File()
            )

print(result.outputs.sorting_out)