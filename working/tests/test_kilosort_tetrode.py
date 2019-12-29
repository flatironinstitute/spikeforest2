#!/usr/bin/env python

from spikeforest2_utils import test_sort_tetrode

def main():
    # I force using singularity for kilosort because on my computer, when docker tries to use gpu it messes up nvidia-container-cli and I need to restart the computer
    import os
    os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'

    # srcdir = os.path.dirname(os.path.realpath(__file__))
    # os.environ['KILOSORT_PATH'] = os.path.join(srcdir, '..', '..', 'spikeforest2', 'sorters', 'kilosort', 'matlab', 'KiloSort')
    # container = None

    container = 'default'

    test_sort_tetrode(sorter_name='kilosort', min_avg_accuracy=0.15, container=container)

if __name__ == '__main__':
    main()