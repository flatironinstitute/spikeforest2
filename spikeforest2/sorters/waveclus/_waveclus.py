import random
import hither

@hither.function('waveclus', '2019.09.23-w1')
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-waveclus:2019.09.23')
@hither.container(default=None)
@hither.local_module('../../../spikeforest2_utils')
@hither.additional_files(['*.m'])
def waveclus(
    recording_path,
    sorting_out
):
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor
    from ._waveclussorter import WaveclusSorter

    recording = AutoRecordingExtractor(dict(path=recording_path), download=True)

    # recording = se.SubRecordingExtractor(parent_recording=recording, start_frame=0, end_frame=30000 * 10)
    
    # Sorting
    print('Sorting...')
    sorter = WaveclusSorter(
        recording=recording,
        output_folder='/tmp/tmp_waveclus_' + _random_string(8),
        delete_output_folder=True
    )

    sorter.set_params(
    )

    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))