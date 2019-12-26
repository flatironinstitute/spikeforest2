import random
import hither

@hither.function('jrclust', '0.0.1-w1')
@hither.output_file('sorting_out')
@hither.container(default='docker://jamesjun/sf-jrclust:0.0.1')
@hither.container(default=None)
@hither.local_module('../../../spikeforest2_utils')
@hither.additional_files(['*.m'])
def jrclust(
    recording_path,
    sorting_out,
    detect_threshold=6,
    car=True, # whether to do common average referencing
    minFR=1/50, # minimum spike rate (Hz), if a cluster falls below this for too long it gets removed
    freq_min=150, # min. bp filter freq (Hz), use 0 for no filter
    sigmaMask=30, # sigmaMask
    nPCs=3, # PCs per channel?
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
        detect_threshold=detect_threshold,
        car=car,
        minFR=minFR,
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