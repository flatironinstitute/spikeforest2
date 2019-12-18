import numpy as np
import hither

def test_sort_tetrode(
    sorter_name,
    min_avg_accuracy
):
    recording_path = 'sha1://961f4a641af64dded4821610189f808f0192de4d/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.json'
    sorting_true_path = 'sha1://cce42806bcfe86f4f58c51aefb61f2c28a99f6cf/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.firings_true.json'
    _test_sort(
        sorter_name=sorter_name,
        min_avg_accuracy=min_avg_accuracy,
        recording_path=recording_path,
        sorting_true_path=sorting_true_path
    )

def test_sort_32c(
    sorter_name,
    min_avg_accuracy
):
    recording_path = 'sha1://17a13b1869b17e4783f3b8c96a58ffa38f25d5e0/PAIRED_KAMPFF/paired_kampff/2015_09_03_Pair_9_0A.json'
    sorting_true_path = 'sha1://2cb5f3cfb67eb4aec6314fb7fa8f8ea906752b35/PAIRED_KAMPFF/paired_kampff/2015_09_03_Pair_9_0A.firings_true.json'
    _test_sort(
        sorter_name=sorter_name,
        min_avg_accuracy=min_avg_accuracy,
        recording_path=recording_path,
        sorting_true_path=sorting_true_path
    )

def _test_sort(
    sorter_name,
    min_avg_accuracy,
    recording_path,
    sorting_true_path
):
    from spikeforest2 import sorters
    from spikeforest2 import processing
    import kachery as ka

    # for now, in this test, don't use gpu for irc
    gpu = sorter_name in ['kilosort2']

    with ka.config(fr='default_readonly'):
        with hither.config(container='default', gpu=gpu):
            sorter = getattr(sorters, sorter_name)
            sorting_result = sorter.run(
                recording_path=recording_path,
                sorting_out=hither.File()
            )

    assert sorting_result.success

    with ka.config(fr='default_readonly'):
        with hither.config(container='default', gpu=False):
            compare_result = processing.compare_with_truth.run(
                sorting_path=sorting_result.outputs.sorting_out,
                sorting_true_path=sorting_true_path,
                json_out=hither.File()
            )

    assert compare_result.success

    obj = ka.load_object(compare_result.outputs.json_out._path)

    aa = _average_accuracy(obj)

    print(F'AVERAGE-ACCURACY: {aa}')

    assert aa >= min_avg_accuracy, f"Average accuracy is lower than expected {aa} < {min_avg_accuracy}"

    print('Passed.')

def _average_accuracy(obj):
    accuracies = [float(obj[i]['accuracy']) for i in obj.keys()]
    return np.mean(accuracies)
