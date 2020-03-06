import os
import random
import hither


@hither.function('spykingcircus', '0.9.5')
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-spykingcircus:0.9.5')
@hither.local_module('../../../spikeforest2_utils')
def spykingcircus(
    recording_path,
    sorting_out,
    detect_sign=-1,
    adjacency_radius=100,
    detect_threshold=6,
    template_width_ms=3,
    filter=True,
    merge_spikes=True,
    auto_merge=0.75,
    whitening_max_elts=1000,
    clustering_max_elts=10000
):
    import spiketoolkit as st
    import spikesorters as ss
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor

    recording = AutoRecordingExtractor(dict(path=recording_path), download=True)
    
    # Sorting
    print('Sorting...')
    sorter = ss.SpykingcircusSorter(
        recording=recording,
        output_folder='/tmp/tmp_spykingcircus_' + _random_string(8),
        delete_output_folder=True
    )

    num_workers = os.environ.get('NUM_WORKERS', None)
    if not num_workers: num_workers='1'
    num_workers = int(num_workers)

    sorter.set_params(
        detect_sign=detect_sign,
        adjacency_radius=adjacency_radius,
        detect_threshold=detect_threshold,
        template_width_ms=template_width_ms,
        filter=filter,
        merge_spikes=merge_spikes,
        auto_merge=auto_merge,
        num_workers=num_workers,
        whitening_max_elts=whitening_max_elts,
        clustering_max_elts=clustering_max_elts
    )     
    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))