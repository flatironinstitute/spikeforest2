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
from hither_sf import ShellScript


def check_if_installed(kilosort_path: Union[str, None]):
    if os.getenv('KILOSORT_BINARY_PATH', None):
        return True
    print(f'Checking if installed: {kilosort_path}')
    if kilosort_path is None:
        return False
    assert isinstance(kilosort_path, str)

    if kilosort_path.startswith('"'):
        kilosort_path = kilosort_path[1:-1]
    kilosort_path = str(Path(kilosort_path).absolute())

    if (Path(kilosort_path) / 'preprocessData.m').is_file():
        return True
    else:
        return False


class KilosortSorter(BaseSorter):
    """
    """

    sorter_name: str = 'kilosort'
    kilosort_path: Union[str, None] = os.getenv('KILOSORT_PATH', None)
    installed = check_if_installed(kilosort_path)
    requires_locations = False

    _default_params = {
        'detect_threshold': 6,
        'Nt': 128 * 1024 * 5 + 64,
        'car': True,
        'useGPU': True,
        'freq_min': 300,
        'freq_max': 6000
    }

    _extra_gui_params = [
        {'name': 'detect_threshold', 'type': 'float', 'value': 6.0, 'default': 6.0, 'title': "Relative detection threshold"},
        {'name': 'Nt', 'type': 'int', 'value': 128 * 1024 * 5 + 64, 'default': 128 * 1024 * 5 + 64, 'title': "Nt - batch size for kilosort"},
        {'name': 'car', 'type': 'bool', 'value': True, 'default': True, 'title': "car"},
        {'name': 'useGPU', 'type': 'bool', 'value': True, 'default': True, 'title': "If True, will use GPU"},
        {'name': 'freq_min', 'type': 'float', 'value': 300.0, 'default': 300.0, 'title': "Low-pass frequency"},
        {'name': 'freq_max', 'type': 'float', 'value': 6000.0, 'default': 6000.0, 'title': "High-pass frequency"},
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
    def set_kilosort_path(kilosort_path: str):
        KilosortSorter.kilosort_path = kilosort_path
        KilosortSorter.installed = check_if_installed(KilosortSorter.kilosort_path)
        try:
            print("Setting KILOSORT_PATH environment variable for subprocess calls to:", kilosort_path)
            os.environ["KILOSORT_PATH"] = kilosort_path
        except Exception as e:
            print("Could not set KILOSORT_PATH environment variable:", e)

    def _setup_recording(self, recording, output_folder):
        # save binary file
        input_file_path = output_folder / 'recording'
        recording.write_to_binary_dat_format(input_file_path, dtype='int16')

    def _run(self, recording, output_folder):
        source_dir = Path(Path(__file__).parent)
        p = self.params

        dat_file=str((output_folder / 'recording.dat').absolute())
        if p['car']:
            use_car = 1
        else:
            use_car = 0
        
        # prepare electrode positions
        if self.grouping_property == 'group' and 'group' in recording.get_shared_channel_property_names():
            groups = recording.get_channel_groups()
        else:
            groups = [1] * recording.get_num_channels()
        if 'location' in recording.get_shared_channel_property_names():
            positions = np.array(recording.get_channel_locations())
            if positions.shape[1] != 2:
                raise RuntimeError("3D 'location' are not supported. Set 2D locations instead")
        else:
            print("'location' information is not found. Using linear configuration")
            positions = np.array(
                [[0, i_ch] for i_ch in range(recording.get_num_channels())])
        xcoords = [positions[i, 0] for i in range(positions.shape[0])]
        ycoords = [positions[i, 1] for i in range(positions.shape[0])]
        kcoords = groups

        nchan = recording.get_num_channels()
        Nfilt = (nchan // 32) * 32 * 8
        if Nfilt == 0:
            Nfilt = nchan * 8

        params0 = dict(
            nchan=recording.get_num_channels(),
            sample_rate=recording.get_sampling_frequency(),
            freq_min=p["freq_min"],
            freq_max=p["freq_max"],
            kilo_thresh=p["detect_threshold"],
            use_car=use_car,
            Nfilt=Nfilt,
            Nt=p["Nt"],
            xcoords=xcoords,
            ycoords=ycoords,
            kcoords=kcoords
        )
        params_path = str(output_folder / 'params.json')
        with open(params_path, 'w') as f:
            json.dump(params0, f)

        if os.getenv('KILOSORT_BINARY_PATH', None):
            shell_cmd = f'''
            #!/bin/bash
            exec $KILOSORT_BINARY_PATH {dat_file} {str(output_folder)} {params_path}
            '''
        else:
            # copy m files
            shutil.copy(str(source_dir / 'matlab' / 'kilosort_master.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'kilosort_config.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'kilosort_channelmap.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'writeNPY.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'constructNPYheader.m'), str(output_folder))
            matlab_script = f'''
            try
                addpath(genpath('{self.kilosort_path}'));
                kilosort_master('{dat_file}', '{str(output_folder)}', '{params_path}')
            catch
                fprintf('----------------------------------------');
                fprintf(lasterr());
                quit(1);
            end
            quit(0);
            '''
            ShellScript(matlab_script).write(str(output_folder / 'kilosort_script.m'))
            if "win" in sys.platform:
                shell_cmd = f'''
                            cd {str(output_folder)}
                            matlab -nosplash -nodisplay -wait -r kilosort_script
                        '''
            else:
                shell_cmd = f'''
                            #!/bin/bash
                            cd "{str(output_folder)}"
                            matlab -nosplash -nodisplay -r kilosort_script
                        '''
        shell_cmd = ShellScript(shell_cmd, redirect_output_to_stdout=True)
        shell_cmd.start()

        retcode = shell_cmd.wait()

        if retcode != 0:
            raise Exception('kilosort returned a non-zero exit code')

    @staticmethod
    def get_result_from_folder(output_folder):
        sorting = se.KiloSortSortingExtractor(folder_path=output_folder)
        return sorting
