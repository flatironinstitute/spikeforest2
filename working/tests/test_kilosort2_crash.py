#!/usr/bin/env python

from spikeforest2_utils import test_sort

def main():
    # I force using singularity for kilosort2 because on my computer, when docker tries to use gpu it messes up nvidia-container-cli and I need to restart the computer
    import os
    os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'
    recording_path = 'sha1://c286dd783e016b91a76d2e8980a23d49fb7cd4e8/PAIRED_CRCNS_HC1/paired_crcns/d11222_d1122207.json'
    sorting_true_path = 'sha1://9f1a7604a9803c41bfc133acea5f78aae23f9d7f/PAIRED_CRCNS_HC1/paired_crcns/d11222_d1122207.firings_true.json'
    test_sort(
        sorter_name='kilosort2',
        min_avg_accuracy=0.1,
        recording_path=recording_path,
        sorting_true_path=sorting_true_path
    )

if __name__ == '__main__':
    main()