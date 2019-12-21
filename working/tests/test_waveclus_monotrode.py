#!/usr/bin/env python

import os
from spikeforest2_utils import test_sort_monotrode

def main():
    inside_container = True

    if inside_container:
        container = 'default'
    else:
        srcdir = os.path.dirname(os.path.realpath(__file__))
        os.environ['WAVECLUS_PATH'] = os.path.join(srcdir, '..', '..', 'spikeforest2', 'sorters', 'waveclus', 'matlab', 'wave_clus')
        container = None

    test_sort_monotrode(sorter_name='waveclus', min_avg_accuracy=0.15, container=container)

if __name__ == '__main__':
    main()