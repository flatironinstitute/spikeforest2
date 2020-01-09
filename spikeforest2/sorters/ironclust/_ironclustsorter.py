import os
from pathlib import Path
from typing import Union
import copy
import sys

import spikeextractors as se
from spikesorters import BaseSorter
from hither import ShellScript


def check_if_installed(ironclust_path: Union[str, None]):
    if os.getenv('IRONCLUST_BINARY_PATH', None):
        return True
    if ironclust_path is None:
        return False
    assert isinstance(ironclust_path, str)

    if ironclust_path.startswith('"'):
        ironclust_path = ironclust_path[1:-1]
    ironclust_path = str(Path(ironclust_path).absolute())

    if (Path(ironclust_path) / 'irc2.m').is_file():
        return True
    else:
        return False


class IronClustSorter(BaseSorter):
    """
    """

    sorter_name: str = 'ironclust'
    ironclust_path: Union[str, None] = os.getenv('IRONCLUST_PATH', None)
    installed = check_if_installed(ironclust_path)
    requires_locations = False    

    _default_params = dict(
        detect_sign=-1,  # Use -1, 0, or 1, depending on the sign of the spikes in the recording
        adjacency_radius=50,  # Use -1 to include all channels in every neighborhood
        adjacency_radius_out=10,  # Use -1 to include all channels in every neighborhood
        detect_threshold=4.5,  # detection threshold
        prm_template_name='',  # .prm template file name
        freq_min=300,
        freq_max=8000,
        merge_thresh=0.99,  # Threshold for automated merging
        pc_per_chan=0,  # Number of principal components per channel
        whiten=False,  # Whether to do channel whitening as part of preprocessing
        filter_type='bandpass',  # none, bandpass, wiener, fftdiff, ndiff
        filter_detect_type='none',  # none, bandpass, wiener, fftdiff, ndiff
        common_ref_type='none',  # none, mean, median
        batch_sec_drift=300,  # batch duration in seconds. clustering time duration
        step_sec_drift=20,  # compute anatomical similarity every n sec
        knn=30,  # K nearest neighbors
        min_count=30,  # Minimum cluster size
        fGpu=True,  # Use GPU if available
        fft_thresh=8,  # FFT-based noise peak threshold
        fft_thresh_low=0,  # FFT-based noise peak lower threshold (set to 0 to disable dual thresholding scheme)
        nSites_whiten=32,  # Number of adjacent channels to whiten
        feature_type='gpca',  # gpca, pca, vpp, vmin, vminmax, cov, energy, xcov
        delta_cut=1,  # Cluster detection threshold (delta-cutoff)
        post_merge_mode=1,  # post merge mode
        sort_mode=1  # sort mode
    )

    _extra_gui_params = [
        {'name': 'detect_sign', 'type': 'int', 'value': -1, 'default': -1,
         'title': "Use -1, 0, or 1, depending on the sign of the spikes in the recording"},
        {'name': 'adjacency_radius', 'type': 'float', 'value': 50.0, 'default': 50.0, 'title': "Use -1 to include all channels in every neighborhood"},
        {'name': 'adjacency_radius_out', 'type': 'float', 'value': 75.0, 'default': 75.0, 'title': "Use -1 to include all channels in every neighborhood"},
        {'name': 'detect_threshold', 'type': 'float', 'value': 4.5, 'default': 4.5, 'title': "Threshold for detection"},
        {'name': 'freq_min', 'type': 'float', 'value': 300.0, 'default': 300.0, 'title': "Low-pass frequency"},
        {'name': 'freq_max', 'type': 'float', 'value': 6000.0, 'default': 6000.0, 'title': "High-pass frequency"},
        {'name': 'prm_template_name', 'type': 'str', 'value': '', 'default': '', 'title': ".prm template file name"},
        {'name': 'merge_thresh', 'type': 'float', 'value': 0.985, 'default': 0.985, 'title': "Threshold for merging"},
        {'name': 'pc_per_chan', 'type': 'int', 'value': 2, 'default': 2, 'title': "Number of principal components per channel"},
        {'name': 'whiten', 'type': 'bool', 'value': True, 'default': True, 'title': "Whitens the recording if True"},
        {'name': 'filter_type', 'type': 'str', 'value': 'bandpass', 'default': 'bandpass', 'title': "none, bandpass, wiener, fftdiff, ndiff"},
        {'name': 'filter_detect_type', 'type': 'str', 'value': 'none', 'default': 'none', 'title': "none, bandpass, wiener, fftdiff, ndiff"},
        {'name': 'common_ref_type', 'type': 'str', 'value': 'none', 'default': 'none', 'title': "none, bandpass, wiener, fftdiff, ndiff"},
        {'name': 'batch_sec_drift', 'type': 'int', 'value': 300, 'default': 300, 'title': "batch duration in seconds. clustering time duration"},
        {'name': 'step_sec_drift', 'type': 'int', 'value': 20, 'default': 20, 'title': "compute anatomical similarity every n sec"},
        {'name': 'knn', 'type': 'int', 'value': 30, 'default': 30, 'title': "K nearest neighbors"},
        {'name': 'min_count', 'type': 'int', 'value': 30, 'default': 30, 'title': "Minimum cluster size"},
        {'name': 'fGpu', 'type': 'bool', 'value': True, 'default': True, 'title': "Use GPU if available"},
        {'name': 'fft_thresh', 'type': 'float', 'value': 8.0, 'default': 8.0, 'title': "FFT-based noise peak threshold"},
        {'name': 'fft_thresh_low', 'type': 'float', 'value': 0.0, 'default': 0.0, 'title': "FFT-based noise peak lower threshold (set to 0 to disable dual thresholding scheme)"},
        {'name': 'nSites_whiten', 'type': 'int', 'value': 32, 'default': 32, 'title': "Number of adjacent channels to whiten"},
        {'name': 'feature_type', 'type': 'str', 'value': 'gpca', 'default': 'gpca', 'title': "gpca, pca, vpp, vmin, vminmax, cov, energy, xcov"},
        {'name': 'delta_cut', 'type': 'int', 'value': 1, 'default': 1, 'title': "Cluster detection threshold (delta-cutoff)"},
        {'name': 'post_merge_mode', 'type': 'int', 'value': 1, 'default': 1, 'title': "post merge mode"},
        {'name': 'sort_mode', 'type': 'int', 'value': 1, 'default': 1, 'title': "sort mode"},
    ]

    sorter_gui_params = copy.deepcopy(BaseSorter.sorter_gui_params)
    for param in _extra_gui_params:
        sorter_gui_params.append(param)

    installation_mesg = ""

    def __init__(self, **kargs):
        BaseSorter.__init__(self, **kargs)

    @staticmethod
    def get_sorter_version():
        return 'unknown'

    def _setup_recording(self, recording: se.RecordingExtractor, output_folder: Path):
        dataset_dir = output_folder / 'ironclust_dataset'
        # Generate three files in the dataset directory: raw.mda, geom.csv, params.json
        # TODO: need to restore _preserve_dtype
        # se.MdaRecordingExtractor.write_recording(recording=recording, save_path=str(dataset_dir), _preserve_dtype=True)
        se.MdaRecordingExtractor.write_recording(recording=recording, save_path=str(dataset_dir))

    def _run(self, recording: se.RecordingExtractor, output_folder: Path):
        dataset_dir = output_folder / 'ironclust_dataset'
        source_dir = Path(__file__).parent

        samplerate = recording.get_sampling_frequency()

        num_channels = recording.get_num_channels()
        num_timepoints = recording.get_num_frames()
        duration_minutes = num_timepoints / samplerate / 60
        if self.verbose:
            print('Num. channels = {}, Num. timepoints = {}, duration = {} minutes'.format(
            num_channels, num_timepoints, duration_minutes))

        if self.verbose:
            print('Creating argfile.txt...')
        txt = ''
        for key0, val0 in self.params.items():
            txt += '{}={}\n'.format(key0, val0)
        txt += 'samplerate={}\n'.format(samplerate)
        with (dataset_dir / 'argfile.txt').open('w') as f:
            f.write(txt)

        tmpdir = output_folder / 'tmp'
        os.makedirs(str(tmpdir), exist_ok=True)
        if self.verbose:
            print('Running ironclust in {tmpdir}...'.format(tmpdir=str(tmpdir)))

        if os.getenv('IRONCLUST_BINARY_PATH', None):
            shell_cmd = f'''
            #!/bin/bash
            cd {tmpdir}
            exec $IRONCLUST_BINARY_PATH {dataset_dir} {tmpdir} {dataset_dir}/argfile.txt
            '''
        else:
            matlab_script = f'''
            try
                addpath(genpath('{self.ironclust_path}'));
                irc2('{dataset_dir}', '{str(tmpdir)}', '{dataset_dir}/argfile.txt')
            catch
                fprintf('----------------------------------------');
                fprintf(lasterr());
                quit(1);
            end
            quit(0);
            '''
            ShellScript(matlab_script).write(str(output_folder / 'ironclust_script.m'))
            if "win" in sys.platform:
                shell_cmd = f'''
                            cd {str(output_folder)}
                            matlab -nosplash -nodisplay -wait -r ironclust_script
                        '''
            else:
                shell_cmd = f'''
                            #!/bin/bash
                            cd "{str(output_folder)}"
                            matlab -nosplash -nodisplay -r ironclust_script
                        '''

        shell_script = ShellScript(shell_cmd, redirect_output_to_stdout=True)
        shell_script.start()

        retcode = shell_script.wait()

        if retcode != 0:
            raise Exception('ironclust returned a non-zero exit code')

        result_fname = str(tmpdir / 'firings.mda')
        if not os.path.exists(result_fname):
            raise Exception('Result file does not exist: ' + result_fname)

        samplerate_fname = str(tmpdir / 'samplerate.txt')
        with open(samplerate_fname, 'w') as f:
            f.write('{}'.format(samplerate))

    @staticmethod
    def get_result_from_folder(output_folder: Union[str, Path]):
        output_folder = Path(output_folder)
        tmpdir = output_folder / 'tmp'

        result_fname = str(tmpdir / 'firings.mda')
        samplerate_fname = str(tmpdir / 'samplerate.txt')
        with open(samplerate_fname, 'r') as f:
            samplerate = float(f.read())

        sorting = se.MdaSortingExtractor(file_path=result_fname, sampling_frequency=samplerate)

        return sorting
