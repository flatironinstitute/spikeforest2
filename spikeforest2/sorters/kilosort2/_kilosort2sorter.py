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


def check_if_installed(kilosort2_path: Union[str, None]):
    if os.getenv('KILOSORT2_BINARY_PATH', None):
        return True
    if kilosort2_path is None:
        return False
    assert isinstance(kilosort2_path, str)

    if kilosort2_path.startswith('"'):
        kilosort2_path = kilosort2_path[1:-1]
    kilosort2_path = str(Path(kilosort2_path).absolute())

    if (Path(kilosort2_path) / 'master_kilosort.m').is_file():
        return True
    else:
        return False


class Kilosort2Sorter(BaseSorter):
    """
    """

    sorter_name: str = 'kilosort2'
    kilosort2_path: Union[str, None] = os.getenv('KILOSORT2_PATH', None)
    installed = check_if_installed(kilosort2_path)
    requires_locations = False

    _default_params = {
        'detect_threshold': 5,
        'projection_threshold': [10, 4],
        'preclust_threshold': 8,
        'car': True,
        'minFR': 0.1,
        'freq_min': 150,
        'sigmaMask': 30,
        'nPCs': 3,
        'Nt': 128 * 1024 * 5 + 64
    }

    _extra_gui_params = [
        {'name': 'detect_threshold', 'type': 'float', 'value': 5.0, 'default': 5.0,
         'title': "Relative detection threshold"},
        {'name': 'projection_threshold', 'type': 'list of float', 'value': [10, 4], 'default': [10, 4],
         'title': "Threshold on projections"},
        {'name': 'preclust_threshold', 'type': 'float', 'value': 8, 'default': 8,
         'title': "Threshold crossings for pre-clustering"},
        {'name': 'car', 'type': 'bool', 'value': True, 'default': True, 'title': "car"},
        {'name': 'minFR', 'type': 'float', 'value': 0.1, 'default': 0.1, 'title': "minFR"},
        {'name': 'freq_min', 'type': 'float', 'value': 150.0, 'default': 150.0, 'title': "Low-pass frequency"},
        {'name': 'sigmaMask', 'type': 'int', 'value': 30, 'default': 30, 'title': "Sigma mask"},
        {'name': 'nPCs', 'type': 'int', 'value': 3, 'default': 3, 'title': "Number of principal components"},
        {'name': 'Nt', 'type': 'int', 'value': 128 * 1024 * 5 + 64, 'default': 128 * 1024 * 5 + 64, 'title': "Nt - batch size for kilosort2"},
    ]

    sorter_gui_params = copy.deepcopy(BaseSorter.sorter_gui_params)
    for param in _extra_gui_params:
        sorter_gui_params.append(param)

    installation_mesg = """\nTo use Kilosort2 run:\n
        >>> git clone https://github.com/MouseLand/Kilosort2
    and provide the installation path by setting the KILOSORT2_PATH
    environment variables or using Kilosort2Sorter.set_kilosort2_path().\n\n

    More information on Kilosort2 at:
        https://github.com/MouseLand/Kilosort2
    """

    def __init__(self, **kargs):
        BaseSorter.__init__(self, **kargs)

    @staticmethod
    def get_sorter_version():
        return 'unknown'

    @staticmethod
    def set_kilosort2_path(kilosort2_path: str):
        Kilosort2Sorter.kilosort2_path = kilosort2_path
        Kilosort2Sorter.installed = check_if_installed(Kilosort2Sorter.kilosort2_path)
        try:
            print("Setting KILOSORT2_PATH environment variable for subprocess calls to:", kilosort2_path)
            os.environ["KILOSORT2_PATH"] = kilosort2_path
        except Exception as e:
            print("Could not set KILOSORT2_PATH environment variable:", e)

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

        params0 = dict(
            nchan=recording.get_num_channels(),
            sample_rate=recording.get_sampling_frequency(),
            freq_min=p["freq_min"],
            projection_threshold=p["projection_threshold"],
            minFR=p["minFR"],
            sigmaMask=p["sigmaMask"],
            preclust_threshold=p["preclust_threshold"],
            kilo_thresh=p["detect_threshold"],
            Nt=p["Nt"],
            use_car=use_car,
            nPCs=p["nPCs"],
            xcoords=xcoords,
            ycoords=ycoords,
            kcoords=kcoords
        )
        params_path = str(output_folder / 'params.json')
        with open(params_path, 'w') as f:
            json.dump(params0, f)

        if os.getenv('KILOSORT2_BINARY_PATH', None):
            shell_cmd = f'''
            #!/bin/bash
            exec $KILOSORT2_BINARY_PATH {dat_file} {str(output_folder)} {params_path}
            '''
        else:
            # copy m files
            shutil.copy(str(source_dir / 'matlab' / 'kilosort2_master.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'kilosort2_config.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'kilosort2_channelmap.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'writeNPY.m'), str(output_folder))
            shutil.copy(str(source_dir / 'matlab' / 'constructNPYheader.m'), str(output_folder))
            matlab_script = f'''
            try
                addpath(genpath('{self.kilosort2_path}'));
                kilosort2_master('{dat_file}', '{str(output_folder)}', '{params_path}')
            catch
                fprintf('----------------------------------------');
                fprintf(lasterr());
                quit(1);
            end
            quit(0);
            '''
            ShellScript(matlab_script).write(str(output_folder / 'kilosort2_script.m'))
            if "win" in sys.platform:
                shell_cmd = f'''
                            cd {str(output_folder)}
                            matlab -nosplash -nodisplay -wait -r kilosort2_script
                        '''
            else:
                shell_cmd = f'''
                            #!/bin/bash
                            cd "{str(output_folder)}"
                            matlab -nosplash -nodisplay -r kilosort2_script
                        '''
        shell_cmd = ShellScript(shell_cmd, redirect_output_to_stdout=True)
        shell_cmd.start()

        retcode = shell_cmd.wait()

        if retcode != 0:
            raise Exception('kilosort2 returned a non-zero exit code')

    @staticmethod
    def get_result_from_folder(output_folder):
        sorting = se.KiloSortSortingExtractor(folder_path=output_folder)
        return sorting
