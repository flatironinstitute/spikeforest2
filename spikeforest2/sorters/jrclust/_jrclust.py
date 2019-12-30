import random
import hither

@hither.function('jrclust', '0.1.0-w1')
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-jrclust:0.1.0')
@hither.container(default=None)
@hither.local_module('../../../spikeforest2_utils')
@hither.additional_files(['*.m'])
def jrclust(
    recording_path,
    sorting_out,
    detect_sign=-1, # Use -1, 0, or 1, depending on the sign of the spikes in the recording')
    adjacency_radius=50,
    detect_threshold=4.5, # detection threshold
    freq_min=300,
    freq_max=3000,
    merge_thresh=0.98,
    pc_per_chan=1,
    filter_type='bandpass', # {none, bandpass, wiener, fftdiff, ndiff}
    nDiffOrder='none',
    min_count=30,
    fGpu=0,
    fParfor=0,
    feature_type='gpca' #  # {gpca, pca, vpp, vmin, vminmax, cov, energy, xcov}')
):
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor
    from ._jrclustsorter import JRClustSorter

    recording = AutoRecordingExtractor(dict(path=recording_path), download=True)

    # recording = se.SubRecordingExtractor(parent_recording=recording, start_frame=0, end_frame=30000 * 10)
    
    # Sorting
    print('Sorting...')
    sorter = JRClustSorter(
        recording=recording,
        output_folder='/tmp/tmp_jrclust_' + _random_string(8),
        delete_output_folder=True
    )

    sorter.set_params(
        detect_sign=detect_sign,
        adjacency_radius=adjacency_radius,
        detect_threshold=detect_threshold,
        freq_min=freq_min,
        freq_max=freq_max,
        merge_thresh=merge_thresh,
        pc_per_chan=pc_per_chan,
        filter_type=filter_type,
        nDiffOrder=nDiffOrder,
        min_count=min_count,
        fGpu=fGpu,
        fParfor=fParfor,
        feature_type=feature_type
    )

    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))