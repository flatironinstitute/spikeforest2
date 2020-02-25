import os
import random
import hither

@hither.function('herdingspikes2', '0.3.7-w1')
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-herdingspikes2:0.3.7')
@hither.local_module('../../../spikeforest2_utils')
def herdingspikes2(
    recording_path,
    sorting_out,
    filter=True,
    pre_scale=True,
    pre_scale_value=20
):
    import spiketoolkit as st
    import spikesorters as ss
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor

    recording = AutoRecordingExtractor(dict(path=recording_path), download=True)
    
    # Sorting
    print('Sorting...')

    output_folder = '/tmp/tmp_herdingspikes2_' + _random_string(8)
    os.environ['HS2_PROBE_PATH'] = output_folder # important for when we are in a container
    sorter = ss.HerdingspikesSorter(
        recording=recording,
        output_folder=output_folder,
        delete_output_folder=True
    )

    num_workers = os.environ.get('NUM_WORKERS', None)
    if not num_workers: num_workers='1'
    num_workers = int(num_workers)

    sorter.set_params(
        filter=filter,
        pre_scale=pre_scale,
        pre_scale_value=pre_scale_value,
        clustering_n_jobs=num_workers
    )
    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))
