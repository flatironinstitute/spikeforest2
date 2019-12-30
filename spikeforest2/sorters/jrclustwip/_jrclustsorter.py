from pathlib import Path
import os
import json
import sys
import numpy as np
from typing import Union
import shutil
import copy

import spikeextractors as se
from spikesorters import BaseSorter
from hither import ShellScript


def check_if_installed(jrclust_path: Union[str, None]):
    if os.getenv('JRCLUST_BINARY_PATH', None):
        return True
    if jrclust_path is None:
        return False
    assert isinstance(jrclust_path, str)

    if jrclust_path.startswith('"'):
        jrclust_path = jrclust_path[1:-1]
    jrclust_path = str(Path(jrclust_path).absolute())

    if (Path(jrclust_path) / 'jrc.m').is_file():
        return True
    else:
        return False


class JRClustSorter(BaseSorter):
    """
    """

    sorter_name: str = 'jrclust'
    jrclust_path: Union[str, None] = os.getenv('JRCLUST_PATH', None)
    installed = check_if_installed(jrclust_path)
    requires_locations = False

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

    @staticmethod
    def set_jrclust_path(jrclust_path: str):
        JRClustSorter.jrclust_path = jrclust_path
        JRClustSorter.installed = check_if_installed(JRClustSorter.jrclust_path)
        try:
            print("Setting JRCLUST_PATH environment variable for subprocess calls to:", jrclust_path)
            os.environ["JRCLUST_PATH"] = jrclust_path
        except Exception as e:
            print("Could not set JRCLUST_PATH environment variable:", e)

    def _setup_recording(self, recording, output_folder):
        # save binary file
        input_file_dir = output_folder / 'recording'
        se.MdaRecordingExtractor.write_recording(recording=recording, save_path=str(input_file_dir))

    def _run(self, recording, output_folder):
        source_dir = Path(Path(__file__).parent)
        p = self.params

        recording_folder=str((output_folder / 'recording').absolute())
        samplerate = recording.get_sampling_frequency()
        txt = ''
        for key0, val0 in p.items():
            txt += '{}={}\n'.format(key0, val0)
        txt += 'samplerate={}\n'.format(samplerate)
        params_file = output_folder / 'argfile.txt'
        with params_file.open('w') as f:
            f.write(txt)

        if os.getenv('JRCLUST_BINARY_PATH', None):
            shell_cmd = f'''
            #!/bin/bash
            exec $JRCLUST_BINARY_PATH {str(recording_folder)} {str(output_folder)} {str(params_file)}
            '''
        else:
            # copy m files
            shutil.copy(str(source_dir / 'matlab' / 'jrclust_binary.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'writemda.m'), str(output_folder))
            matlab_script = f'''
            addpath(genpath('{self.jrclust_path}'));
            jrclust_binary('{str(recording_folder)}', '{str(output_folder)}', '{str(params_file)}')
            '''
            ShellScript(matlab_script).write(str(output_folder / 'jrclust_script.m'))
            if "win" in sys.platform:
                shell_cmd = f'''
                            cd {str(output_folder)}
                            matlab -nosplash -nodisplay -wait -r jrclust_script
                        '''
            else:
                shell_cmd = f'''
                            #!/bin/bash
                            cd "{str(output_folder)}"
                            matlab -nosplash -nodisplay -r jrclust_script
                        '''
        shell_cmd = ShellScript(shell_cmd, redirect_output_to_stdout=True)
        shell_cmd.start()

        retcode = shell_cmd.wait()

        if retcode != 0:
            raise Exception('jrclust returned a non-zero exit code')

    @staticmethod
    def get_result_from_folder(output_folder):
        sorting = se.MdaSortingExtractor(file_path=str(output_folder / 'firings.mda'))
        return sorting