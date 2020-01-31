import os
import random
import hither

@hither.function('tridesclous', '1.4.2-w1')
@hither.output_file('sorting_out')
#@hither.container(default='docker://magland/sf-tridesclous:1.4.2')
@hither.container(default='docker://samuelgarcialyon/sf-tridesclous:1.4.2')
@hither.local_module('../../../spikeforest2_utils')
def tridesclous(
    recording_path,
    sorting_out
):
    import spiketoolkit as st
    import spikesorters as ss
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor

    recording = AutoRecordingExtractor(dict(path=recording_path), download=True)
    
    # Sorting
    print('Sorting...')

    output_folder = '/tmp/tmp_tridesclous_' + _random_string(8)
    os.environ['HS2_PROBE_PATH'] = output_folder # important for when we are in a container
    sorter = ss.TridesclousSorter(
        recording=recording,
        output_folder=output_folder,
        delete_output_folder=True,
        verbose=True,
    )

    # num_workers = os.environ.get('NUM_WORKERS', None)
    # if not num_workers: num_workers='1'
    # num_workers = int(num_workers)

    sorter.set_params(
    )
    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))