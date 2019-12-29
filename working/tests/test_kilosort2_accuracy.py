#!/usr/bin/env python

from spikeforest2_utils import test_sort

def main():
    # I force using singularity for kilosort2 because on my computer, when docker tries to use gpu it messes up nvidia-container-cli and I need to restart the computer
    import os
    os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'
    recording_path = 'sha1://9f0980baf3d831262c61a20649b1c8be868d6be2/PAIRED_BOYDEN/paired_boyden32c/419_1_8.json'
    sorting_true_path = 'sha1://7406448fce8c4bf9b25ece793b03095698b47cd7/PAIRED_BOYDEN/paired_boyden32c/419_1_8.firings_true.json'
    test_sort(
        sorter_name='kilosort2',
        min_avg_accuracy=0.1,
        recording_path=recording_path,
        sorting_true_path=sorting_true_path
    )

if __name__ == '__main__':
    main()