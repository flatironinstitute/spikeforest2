#!/usr/bin/env python

from spikeforest2_utils import test_sort_tetrode

def main():
    test_sort_tetrode(sorter_name='tridesclous', min_avg_accuracy=0.2)

if __name__ == '__main__':
    main()