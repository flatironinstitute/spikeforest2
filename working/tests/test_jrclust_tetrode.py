#!/usr/bin/env python

from spikeforest2_utils import test_sort_tetrode

def main():
    import os

    os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'
    container='default'
    
    test_sort_tetrode(sorter_name='jrclust', min_avg_accuracy=0.25, container=container)

if __name__ == '__main__':
    main()