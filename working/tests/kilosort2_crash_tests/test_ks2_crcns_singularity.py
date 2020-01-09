#!/usr/bin/env python

import numpy as np
from spikeforest2 import sorters
from spikeforest2 import processing
import hither
import kachery as ka
import os

os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'

recording_path = 'sha1dir://779d96521176077ec260ef99573dea3b772c74e6.paired_crcns/d18811_d18811.001'
sorting_true_path = 'sha1dir://779d96521176077ec260ef99573dea3b772c74e6.paired_crcns/d18811_d18811.001/firings_true.mda'

sorter_name = 'kilosort2'
sorter = getattr(sorters, sorter_name)
params = {}

# Determine whether we are going to use gpu based on the name of the sorter
gpu = sorter_name in ['kilosort2', 'kilosort', 'tridesclous', 'ironclust']

# In the future we will check whether we have the correct version of the wrapper here
# Version: 0.1.5-w1

# Download the data (if needed)
ka.set_config(fr='default_readonly')
ka.load_file(recording_path + '/raw.mda')

# Run the spike sorting
with hither.config(container='default', gpu=gpu):
  sorting_result = sorter.run(
    recording_path=recording_path,
    sorting_out=hither.File(),
    **params
  )
assert sorting_result.success
sorting_path = sorting_result.outputs.sorting_out

# Compare with ground truth
with hither.config(container='default'):
  compare_result = processing.compare_with_truth.run(
    sorting_path=sorting_path,
    sorting_true_path=sorting_true_path,
    json_out=hither.File()
  )
assert compare_result.success
obj = ka.load_object(compare_result.outputs.json_out._path)

accuracies = [float(obj[i]['accuracy']) for i in obj.keys()]
print('ACCURACIES:')
print(accuracies)
print('')

average_accuracy = np.mean(accuracies)
print('AVERAGE-ACCURACY:', average_accuracy)