import random
import hither

@hither.function('ironclust', '5.0.5-w1')
@hither.input_file('recording', kachery_resolve=False)
@hither.output_file('sorting_out')
@hither.container(default='docker://magland/sf-ironclust:5.0.5')
@hither.local_module('../../../spikeforest2_utils')
def ironclust(recording, sorting_out):
    import spiketoolkit as st
    import spikesorters as ss
    import spikeextractors as se
    from spikeforest2_utils import AutoRecordingExtractor
    import kachery as ka
    from ._ironclustsorter import IronClustSorter

    # TODO: need to think about how to deal with this
    ka.set_config(fr='default_readonly')

    recording = AutoRecordingExtractor(dict(path=recording), download=True)

    # Sorting
    print('Sorting...')
    sorter = IronClustSorter(
        recording=recording,
        output_folder='/tmp/tmp_ironclust_' + _random_string(8),
        delete_output_folder=True
    )

    sorter.set_params(
        detect_sign=-1,
        adjacency_radius=50,
        adjacency_radius_out=75,
        detect_threshold=4,
        prm_template_name='',
        freq_min=300,
        freq_max=8000,
        merge_thresh=0.99,
        pc_per_chan=0,
        whiten=False,
        filter_type='bandpass',
        filter_detect_type='none',
        common_ref_type='mean',
        batch_sec_drift=300,
        step_sec_drift=20,
        knn=30,
        min_count=30,
        fGpu=True,
        fft_thresh=8,
        fft_thresh_low=0,
        nSites_whiten=32,
        feature_type='gpca',
        delta_cut=1,
        post_merge_mode=1,
        sort_mode=1
    )     
    timer = sorter.run()
    print('#SF-SORTER-RUNTIME#{:.3f}#'.format(timer))
    sorting = sorter.get_result()

    se.MdaSortingExtractor.write_sorting(sorting=sorting, save_path=sorting_out)

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))