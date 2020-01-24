#!/usr/bin/env python

from spikeforest2_utils import test_sort_monotrode

def main():
    test_sort_monotrode(sorter_name='ironclust', min_avg_accuracy=0.4)

if __name__ == '__main__':
    main()