#!/usr/bin/env python

from spikeforest2 import sorters
import hither
import kachery as ka

recording_path = 'sha1://961f4a641af64dded4821610189f808f0192de4d/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.json'

with ka.config(fr='default_readonly'):
    with hither.config(container='default', gpu=False, job_timeout=5, exception_on_fail=False):
        result = sorters.mountainsort4.run(
            recording_path=recording_path,
            sorting_out=hither.File()
        )

print('Status: ', result.status)
print('Success: ', result.success)
print('Timed out:', result.runtime_info['timed_out'])

assert result.status == 'error'
assert result.success is False
assert result.runtime_info['timed_out'] is True

print('Passed.')