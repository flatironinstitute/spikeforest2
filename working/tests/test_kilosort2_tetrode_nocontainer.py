#!/usr/bin/env python

from spikeforest2_utils import test_sort_tetrode

def main():
    # I force using singularity for kilosort2 because on my computer, when docker tries to use gpu it messes up nvidia-container-cli and I need to restart the computer
    import os
    os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'
    srcdir = os.path.dirname(os.path.realpath(__file__))
    os.environ['KILOSORT2_PATH'] = os.path.join(srcdir, '..', '..', 'spikeforest2', 'sorters', 'kilosort2', 'matlab', 'Kilosort2')
    test_sort_tetrode(sorter_name='kilosort2', min_avg_accuracy=0.15, container=None)

if __name__ == '__main__':
    main()