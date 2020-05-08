import random
import hither_sf as hither

@hither.function('kilosort', '0.1.0-w1')
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-kilosort:0.1.0')
@hither.container(default=None)
@hither.local_module('../../../spikeforest2_utils')
@hither.additional_files(['*.m'])
def kilosort(
    recording_path,
    sorting_out,
    detect_threshold=6,
    freq_min=300,
    freq_max=6000,
    Nt=128 * 1024 * 5 + 64 # batch size for kilosort
):
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor
    from ._kilosortsorter import KilosortSorter

    recording = AutoRecordingExtractor(dict(path=recording_path), download=True)

    # recording = se.SubRecordingExtractor(parent_recording=recording, start_frame=0, end_frame=30000 * 10)
    
    # Sorting
    print('Sorting...')
    sorter = KilosortSorter(
        recording=recording,
        output_folder='/tmp/tmp_kilosort_' + _random_string(8),
        delete_output_folder=True
    )

    sorter.set_params(
        detect_threshold=detect_threshold,
        freq_min=freq_min,
        freq_max=freq_max,
        car=True
    )

    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))