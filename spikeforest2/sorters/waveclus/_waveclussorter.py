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


def check_if_installed(waveclus_path: Union[str, None]):
    if os.getenv('WAVECLUS_BINARY_PATH', None):
        return True
    if waveclus_path is None:
        return False
    assert isinstance(waveclus_path, str)

    if waveclus_path.startswith('"'):
        waveclus_path = waveclus_path[1:-1]
    waveclus_path = str(Path(waveclus_path).absolute())

    if (Path(waveclus_path) / 'wave_clus.m').is_file():
        return True
    else:
        return False


class WaveclusSorter(BaseSorter):
    """
    """

    sorter_name: str = 'waveclus'
    waveclus_path: Union[str, None] = os.getenv('WAVECLUS_PATH', None)
    installed = check_if_installed(waveclus_path)
    requires_locations = False

    _default_params = {
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

    @staticmethod
    def set_waveclus_path(waveclus_path: str):
        WaveclusSorter.waveclus_path = waveclus_path
        WaveclusSorter.installed = check_if_installed(WaveclusSorter.waveclus_path)
        try:
            print("Setting WAVECLUS_PATH environment variable for subprocess calls to:", waveclus_path)
            os.environ["WAVECLUS_PATH"] = waveclus_path
        except Exception as e:
            print("Could not set WAVECLUS_PATH environment variable:", e)

    def _setup_recording(self, recording, output_folder):
        # save binary file
        input_file_dir = output_folder / 'recording'
        se.MdaRecordingExtractor.write_recording(recording=recording, save_path=str(input_file_dir))

    def _run(self, recording, output_folder):
        source_dir = Path(Path(__file__).parent)
        p = self.params

        dat_file=str((output_folder / 'recording/raw.mda').absolute())

        if os.getenv('WAVECLUS_BINARY_PATH', None):
            shell_cmd = f'''
            #!/bin/bash
            exec $WAVECLUS_BINARY_PATH {str(output_folder)} {dat_file} {str(output_folder)}/firings.mda {recording.get_sampling_frequency()}
            '''
        else:
            # copy m files
            shutil.copy(str(source_dir / 'matlab' / 'waveclus_binary.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'readmda.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'writemda.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'set_parameters_spf.m'), str(output_folder))
            matlab_script = f'''
            addpath(genpath('{self.waveclus_path}'));
            waveclus_binary('{str(output_folder)}', '{dat_file}', '{str(output_folder)}/firings.mda', {recording.get_sampling_frequency()})
            '''
            ShellScript(matlab_script).write(str(output_folder / 'waveclus_script.m'))
            if "win" in sys.platform:
                shell_cmd = f'''
                            cd {str(output_folder)}
                            matlab -nosplash -nodisplay -wait -r waveclus_script
                        '''
            else:
                shell_cmd = f'''
                            #!/bin/bash
                            cd "{str(output_folder)}"
                            matlab -nosplash -nodisplay -r waveclus_script
                        '''
        shell_cmd = ShellScript(shell_cmd, redirect_output_to_stdout=True)
        shell_cmd.start()

        retcode = shell_cmd.wait()

        if retcode != 0:
            raise Exception('waveclus returned a non-zero exit code')

    @staticmethod
    def get_result_from_folder(output_folder):
        sorting = se.MdaSortingExtractor(file_path=str(output_folder / 'firings.mda'))
        return sorting