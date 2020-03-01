import random
import hither

@hither.function('ironclust', '5.9.6-w1')
@hither.output_file('sorting_out')
@hither.container(default='docker://jamesjun/sf-ironclust:5.9.6')
@hither.local_module('../../../spikeforest2_utils')
def ironclust(recording_path, sorting_out, 
    detect_threshold=3.5, freq_min=300, freq_max=8000, detect_sign=-1, adjacency_radius=50, whiten=False,
    adjacency_radius_out=100, merge_thresh=0.98, fft_thresh=8, knn=30, min_count=30, delta_cut=1,    
    pc_per_chan=9, batch_sec_drift=300, step_sec_drift=20,
    common_ref_type='trimmean', fGpu=True, clip_pre=0.25, clip_post=0.75, 
    merge_thresh_cc=1, nRepeat_merge=3, merge_overlap_thresh=.95
):

    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor
    from ._ironclustsorter import IronClustSorter

    recording = AutoRecordingExtractor(dict(path=recording_path), download=True)
    
    # Sorting
    print('Sorting...')
    sorter = IronClustSorter(
        recording=recording,
        output_folder='/tmp/tmp_ironclust_' + _random_string(8),
        delete_output_folder=True
    )

    sorter.set_params(
        fft_thresh_low=0, nSites_whiten=32, feature_type='gpca', post_merge_mode=1, sort_mode=1, prm_template_name='', filter_type='bandpass', filter_detect_type='none',
        detect_threshold=detect_threshold, freq_min=freq_min, freq_max=freq_max, detect_sign=detect_sign, adjacency_radius=adjacency_radius, whiten=whiten,
        adjacency_radius_out=adjacency_radius_out, merge_thresh=merge_thresh, fft_thresh=fft_thresh, knn=knn, min_count=min_count, delta_cut=delta_cut,
        pc_per_chan=pc_per_chan, batch_sec_drift=batch_sec_drift, step_sec_drift=step_sec_drift, 
        common_ref_type=common_ref_type, fGpu=fGpu, clip_pre=clip_pre, clip_post=clip_post, 
        merge_thresh_cc=merge_thresh_cc, nRepeat_merge=3, merge_overlap_thresh=.95
    )     
    timer = sorter.run()
    #print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))