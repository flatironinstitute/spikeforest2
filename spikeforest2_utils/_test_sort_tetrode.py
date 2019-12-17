import numpy as np
import hither

def test_sort_tetrode(
    sorter_name,
    min_avg_accuracy
):
    from spikeforest2 import sorters
    from spikeforest2 import processing
    import kachery as ka

    recording_path = 'sha1://961f4a641af64dded4821610189f808f0192de4d/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.json'
    sorting_true_path = 'sha1://cce42806bcfe86f4f58c51aefb61f2c28a99f6cf/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.firings_true.json'

    with ka.config(fr='default_readonly'):
        with hither.config(container='default', gpu=False):
            sorter = getattr(sorters, sorter_name)
            sorting_result = sorter.run(
                recording_path=recording_path,
                sorting_out=hither.File()
            )

    assert sorting_result.success

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
