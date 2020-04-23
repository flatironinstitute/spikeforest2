import numpy as np

def test_sort_tetrode(
    sorter_name,
    min_avg_accuracy,
    num_jobs=1,
    job_handler=None,
    container='default'
):
    recording_path = 'sha1://961f4a641af64dded4821610189f808f0192de4d/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.json'
    sorting_true_path = 'sha1://cce42806bcfe86f4f58c51aefb61f2c28a99f6cf/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.firings_true.json'
    test_sort(
        sorter_name=sorter_name,
        min_avg_accuracy=min_avg_accuracy,
        recording_path=recording_path,
        sorting_true_path=sorting_true_path,
        num_jobs=num_jobs,
        job_handler=job_handler,
        container=container
    )

def test_sort_32c(
    sorter_name,
    min_avg_accuracy,
    num_jobs=1,
    job_handler=None,
    container='default'
):
    recording_path = 'sha1://17a13b1869b17e4783f3b8c96a58ffa38f25d5e0/PAIRED_KAMPFF/paired_kampff/2015_09_03_Pair_9_0A.json'
    sorting_true_path = 'sha1://2cb5f3cfb67eb4aec6314fb7fa8f8ea906752b35/PAIRED_KAMPFF/paired_kampff/2015_09_03_Pair_9_0A.firings_true.json'
    test_sort(
        sorter_name=sorter_name,
        min_avg_accuracy=min_avg_accuracy,
        recording_path=recording_path,
        sorting_true_path=sorting_true_path,
        num_jobs=num_jobs,
        job_handler=job_handler,
        container=container
    )

def test_sort_monotrode(
    sorter_name,
    min_avg_accuracy,
    num_jobs=1,
    job_handler=None,
    container='default'
):
    recording_path = 'sha1://34e73017bc6770946c2e3b3d6ec8260f9ce42280/PAIRED_MONOTRODE/paired_monotrode_boyden32c/1103_1_1_ch1.json'
    sorting_true_path = 'sha1://f023cc44216b60084ef7b710039ec6642b76d93f/PAIRED_MONOTRODE/paired_monotrode_boyden32c/1103_1_1_ch1.firings_true.json'
    test_sort(
        sorter_name=sorter_name,
        min_avg_accuracy=min_avg_accuracy,
        recording_path=recording_path,
        sorting_true_path=sorting_true_path,
        num_jobs=num_jobs,
        job_handler=job_handler,
        container=container
    )

def test_sort(
    sorter_name,
    min_avg_accuracy,
    recording_path,
    sorting_true_path,
    num_jobs=1,
    job_handler=None,
    container='default'
):
    from spikeforest2 import sorters
    from spikeforest2 import processing
    import hither
    import kachery as ka

    # for now, in this test, don't use gpu for irc
    gpu = sorter_name in ['kilosort2', 'kilosort', 'tridesclous', 'ironclust']

    sorting_results = []
    with ka.config(fr='default_readonly'):
        with hither.config(container=container, gpu=gpu, job_handler=job_handler), hither.job_queue():
            sorter = getattr(sorters, sorter_name)
            for _ in range(num_jobs):
                sorting_result = sorter.run(
                    recording_path=recording_path,
                    sorting_out=hither.File()
                )
                sorting_results.append(sorting_result)

    assert sorting_result.success

    sorting_result = sorting_results[0]
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
