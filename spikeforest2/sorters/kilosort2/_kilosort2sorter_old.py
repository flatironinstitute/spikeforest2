import os
from pathlib import Path
from typing import Union
import copy
import sys

import spikeextractors as se
from spikesorters import BaseSorter
from hither import ShellScript


class Kilosort2Sorter(BaseSorter):
    """
    """

    sorter_name: str = 'kilosort2'
    installed = True
    requires_locations = True

    _default_params = {
        'detect_sign': -1,
        'detect_threshold': 5,
        'freq_min': 150,
        'pc_per_chan': 3
    }

    _extra_gui_params = [
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
        dataset_dir = output_folder / 'kilosort2_dataset'
        # Generate three files in the dataset directory: raw.mda, geom.csv, params.json
        # TODO: need to restore _preserve_dtype
        # se.MdaRecordingExtractor.write_recording(recording=recording, save_path=str(dataset_dir), _preserve_dtype=True)
        se.MdaRecordingExtractor.write_recording(recording=recording, save_path=str(dataset_dir))

    def _run(self, recording: se.RecordingExtractor, output_folder: Path):
        dataset_dir = output_folder / 'kilosort2_dataset'
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
            print('Running kilosort2 in {tmpdir}...'.format(tmpdir=str(tmpdir)))

        shell_cmd = '''
            #!/bin/bash
            cd {tmpdir}
            exec /run_ksort2 {dataset_dir} {tmpdir} {dataset_dir}/argfile.txt
        '''.format(tmpdir=str(tmpdir), dataset_dir=str(dataset_dir))

        shell_script = ShellScript(shell_cmd, redirect_output_to_stdout=True)
        shell_script.start()

        retcode = shell_script.wait()

        if retcode != 0:
            raise Exception('kilosort2 returned a non-zero exit code')

        result_fname = str(tmpdir / 'firings_out.mda')
        if not os.path.exists(result_fname):
            raise Exception('Result file does not exist: ' + result_fname)

        samplerate_fname = str(tmpdir / 'samplerate.txt')
        with open(samplerate_fname, 'w') as f:
            f.write('{}'.format(samplerate))

    @staticmethod
    def get_result_from_folder(output_folder: Union[str, Path]):
        output_folder = Path(output_folder)
        tmpdir = output_folder / 'tmp'

        result_fname = str(tmpdir / 'firings_out.mda')
        samplerate_fname = str(tmpdir / 'samplerate.txt')
        with open(samplerate_fname, 'r') as f:
            samplerate = float(f.read())

        sorting = se.MdaSortingExtractor(file_path=result_fname, sampling_frequency=samplerate)

        return sorting
