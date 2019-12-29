import os
from pathlib import Path
from typing import Union
import copy
import sys

import spikeextractors as se
from spikesorters import BaseSorter
from hither import ShellScript


class JRClustSorter(BaseSorter):
    """
    """

    sorter_name: str = 'jrclust'
    installed = True
    requires_locations = True

    _default_params = dict(
        detect_sign=-1,  # Use -1, 0, or 1, depending on the sign of the spikes in the recording
        adjacency_radius=50,  # Use -1 to include all channels in every neighborhood
        detect_threshold=4.5,  # detection threshold
        freq_min=300,
        freq_max=3000,
        merge_thresh=0.98,  # Threshold for automated merging
        pc_per_chan=1,  # Number of principal components per channel
        filter_type='bandpass',  # none, bandpass, wiener, fftdiff, ndiff
        nDiffOrder = 2,
        common_ref_type='none',  # none, mean, median
        min_count=30,  # Minimum cluster size
        fGpu=True,  # Use GPU if available
        fParfor=False, #do not use parfor due slow start-up time
        fft_thresh=8,  # FFT-based noise peak threshold
        feature_type='gpca',  # gpca, pca, vpp, vmin, vminmax, cov, energy, xcov
    )

    _extra_gui_params = [
        {'name': 'detect_sign', 'type': 'int', 'value': -1, 'default': -1,
         'title': "Use -1, 0, or 1, depending on the sign of the spikes in the recording"},
        {'name': 'adjacency_radius', 'type': 'float', 'value': 50.0, 'default': 50.0, 'title': "Use -1 to include all channels in every neighborhood"},
        {'name': 'detect_threshold', 'type': 'float', 'value': 4.5, 'default': 4.5, 'title': "Threshold for detection"},
        {'name': 'freq_min', 'type': 'float', 'value': 300.0, 'default': 300.0, 'title': "Low-pass frequency"},
        {'name': 'freq_max', 'type': 'float', 'value': 6000.0, 'default': 6000.0, 'title': "High-pass frequency"},
        {'name': 'merge_thresh', 'type': 'float', 'value': 0.985, 'default': 0.985, 'title': "Threshold for merging"},
        {'name': 'pc_per_chan', 'type': 'int', 'value': 2, 'default': 2, 'title': "Number of principal components per channel"},
        {'name': 'filter_type', 'type': 'str', 'value': 'bandpass', 'default': 'bandpass', 'title': "none, bandpass, wiener, fftdiff, ndiff"},
        {'name': 'nDiffOrder', 'type': 'int', 'value': '2', 'default': '2', 'title': "Differentiator filter order"},
        {'name': 'common_ref_type', 'type': 'str', 'value': 'none', 'default': 'none', 'title': "none, bandpass, wiener, fftdiff, ndiff"},
        {'name': 'min_count', 'type': 'int', 'value': 30, 'default': 30, 'title': "Minimum cluster size"},
        {'name': 'fGpu', 'type': 'bool', 'value': True, 'default': True, 'title': "Use GPU if available"},
        {'name': 'fft_thresh', 'type': 'float', 'value': 8.0, 'default': 8.0, 'title': "FFT-based noise peak threshold"},
        {'name': 'fft_thresh_low', 'type': 'float', 'value': 0.0, 'default': 0.0, 'title': "FFT-based noise peak lower threshold (set to 0 to disable dual thresholding scheme)"},
        {'name': 'nSites_whiten', 'type': 'int', 'value': 32, 'default': 32, 'title': "Number of adjacent channels to whiten"},
        {'name': 'feature_type', 'type': 'str', 'value': 'gpca', 'default': 'gpca', 'title': "gpca, pca, vpp, vmin, vminmax, cov, energy, xcov"},
    ]

    sorter_gui_params = copy.deepcopy(BaseSorter.sorter_gui_params)
    for param in _extra_gui_params:
        sorter_gui_params.append(param)

    installation_mesg = ""

    def __init__(self, **kargs):
        BaseSorter.__init__(self, **kargs)

    @staticmethod
    def get_sorter_version():
        return '4.0.1'

    def _setup_recording(self, recording: se.RecordingExtractor, output_folder: Path):
        dataset_dir = output_folder / 'jrclust_dataset'
        # Generate three files in the dataset directory: raw.mda, geom.csv, params.json
        # TODO: need to restore _preserve_dtype
        # se.MdaRecordingExtractor.write_recording(recording=recording, save_path=str(dataset_dir), _preserve_dtype=True)
        se.MdaRecordingExtractor.write_recording(recording=recording, save_path=str(dataset_dir))

    def _run(self, recording: se.RecordingExtractor, output_folder: Path):
        dataset_dir = output_folder / 'jrclust_dataset'
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
            print('Running jrclust in {tmpdir}...'.format(tmpdir=str(tmpdir)))

        shell_cmd = '''
            #!/bin/bash
            cd {tmpdir}
            exec /run_irc {dataset_dir} {tmpdir} {dataset_dir}/argfile.txt
        '''.format(tmpdir=str(tmpdir), dataset_dir=str(dataset_dir))

        shell_script = ShellScript(shell_cmd, redirect_output_to_stdout=True)
        shell_script.start()

        retcode = shell_script.wait()

        if retcode != 0:
            raise Exception('jrclust returned a non-zero exit code')

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
