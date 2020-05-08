import os
import random
import hither_sf as hither

@hither.function('klusta', '3.0.16-w1')
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-klusta:3.0.16')
@hither.local_module('../../../spikeforest2_utils')
def klusta(
    recording_path,
    sorting_out,
    adjacency_radius=None,
    detect_sign=-1,
    threshold_strong_std_factor=5,
    threshold_weak_std_factor=2,
    n_features_per_channel=3,
    num_starting_clusters=3,
    extract_s_before=16,
    extract_s_after=32
):
    import spikesorters as ss
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor

    recording = AutoRecordingExtractor(dict(path=recording_path), download=True)
    
    # Sorting
    print('Sorting...')
    sorter = ss.KlustaSorter(
        recording=recording,
        output_folder='/tmp/tmp_klusta_' + _random_string(8),
        delete_output_folder=True
    )

    # num_workers = os.environ.get('NUM_WORKERS', None)
    # if not num_workers: num_workers='1'
    # num_workers = int(num_workers)

    sorter.set_params(
        adjacency_radius=adjacency_radius,
        detect_sign=detect_sign,
        threshold_strong_std_factor=threshold_strong_std_factor,
        threshold_weak_std_factor=threshold_weak_std_factor,
        n_features_per_channel=n_features_per_channel,
        num_starting_clusters=num_starting_clusters,
        extract_s_before=extract_s_before,
        extract_s_after=extract_s_after
    )     
    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))