import random
import hither

@hither.function('kilosort2', '0.1.0-w1')
@hither.input_file('recording', kachery_resolve=False)
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-kilosort2:0.1.0')
@hither.local_module('../../../spikeforest2_utils')
def kilosort2(recording, sorting_out):
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor
    from ._kilosort2sorter import Kilosort2Sorter
    import kachery as ka

    # TODO: need to think about how to deal with this
    ka.set_config(fr='default_readonly')

    recording = AutoRecordingExtractor(dict(path=recording), download=True)

    # recording = se.SubRecordingExtractor(parent_recording=recording, start_frame=0, end_frame=30000 * 10)
    
    # Sorting
    print('Sorting...')
    sorter = Kilosort2Sorter(
        recording=recording,
        output_folder='/tmp/tmp_kilosort2_' + _random_string(8),
        delete_output_folder=True
    )

    sorter.set_params(
        detect_sign=-1,
        detect_threshold=5,
        freq_min=150,
        pc_per_chan=3
    )     
    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))