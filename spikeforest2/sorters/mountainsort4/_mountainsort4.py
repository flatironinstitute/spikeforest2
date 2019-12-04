import json
import random
import hither

@hither.function('mountainsort4', '0.3.2-w3')
@hither.input_file('recording', kachery_resolve=False)
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-mountainsort4:0.3.2')
@hither.local_module('../../../spikeforest2_utils')
def mountainsort4(recording: str, sorting_out: str) -> str:
    import spiketoolkit as st
    import spikesorters as ss
    from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor
    import kachery as ka

    # TODO: need to think about how to deal with this
    ka.set_config(fr='default_readonly')

    recording = AutoRecordingExtractor(dict(path=recording), download=True)

    # recording = se.SubRecordingExtractor(parent_recording=recording, start_frame=0, end_frame=30000 * 10)
    
    # Preprocessing
    print('Preprocessing...')
    recording = st.preprocessing.bandpass_filter(recording, freq_min=300, freq_max=6000)
    recording = st.preprocessing.whiten(recording)

    # Sorting
    print('Sorting...')
    sorter = ss.Mountainsort4Sorter(
        recording=recording,
        output_folder='/tmp/tmp_mountainsort4_' + _random_string(8),
        delete_output_folder=True
    )

    sorter.set_params(
        detect_sign=-1,
        adjacency_radius=50,
        detect_threshold=4
    )     
    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    AutoSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))