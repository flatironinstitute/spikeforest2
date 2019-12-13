import random
import hither

@hither.function('kilosort2', '0.1.0-w2')
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-kilosort2:0.1.0')
@hither.local_module('../../../spikeforest2_utils')
def kilosort2(
    recording_path,
    sorting_out,
    detect_threshold=6,
    car=True, # whether to do common average referencing
    minFR=1/50, # minimum spike rate (Hz), if a cluster falls below this for too long it gets removed
    electrode_dimensions=None,
    freq_min=150, # min. bp filter freq (Hz), use 0 for no filter
    sigmaMask=30, # sigmaMask
    nPCs=3, # PCs per channel?
):
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor
    from ._kilosort2sorter import Kilosort2Sorter

    recording = AutoRecordingExtractor(dict(path=recording_path), download=True)

    # recording = se.SubRecordingExtractor(parent_recording=recording, start_frame=0, end_frame=30000 * 10)
    
    # Sorting
    print('Sorting...')
    sorter = Kilosort2Sorter(
        recording=recording,
        output_folder='/tmp/tmp_kilosort2_' + _random_string(8),
        delete_output_folder=True
    )

    sorter.set_params(
        detect_threshold=detect_threshold,
        car=car,
        minFR=minFR,
        electrode_dimensions=electrode_dimensions,
        freq_min=freq_min,
        sigmaMask=sigmaMask,
        nPCs=nPCs
    )

    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))