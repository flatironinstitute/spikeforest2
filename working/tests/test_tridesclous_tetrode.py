#!/usr/bin/env python

import os
from spikeforest2_utils import test_sort_tetrode

def main():
    os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'
    test_sort_tetrode(sorter_name='tridesclous', min_avg_accuracy=0.05)

if __name__ == '__main__':
    main()