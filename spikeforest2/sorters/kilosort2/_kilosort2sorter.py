from pathlib import Path
import os
import sys
import numpy as np
from typing import Union
import shutil
import copy

import spikeextractors as se
from spikesorters import BaseSorter
from hither import ShellScript


def check_if_installed(kilosort2_path: Union[str, None]):
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
        'nPCs': 3
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
        source_dir = Path(Path(__file__).parent)
        p = self.params

        if not check_if_installed(Kilosort2Sorter.kilosort2_path):
            raise Exception(Kilosort2Sorter.installation_mesg)
        assert isinstance(Kilosort2Sorter.kilosort2_path, str)

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

        # save binary file
        input_file_path = output_folder / 'recording'
        recording.write_to_binary_dat_format(input_file_path, dtype='int16')

        if p['car']:
            use_car = 1
        else:
            use_car = 0

        # read the template txt files
        with (source_dir / 'kilosort2_master.m').open('r') as f:
            kilosort2_master_txt = f.read()
        with (source_dir / 'kilosort2_config.m').open('r') as f:
            kilosort2_config_txt = f.read()
        with (source_dir / 'kilosort2_channelmap.m').open('r') as f:
            kilosort2_channelmap_txt = f.read()

        # make substitutions in txt files
        kilosort2_master_txt = kilosort2_master_txt.format(
            kilosort2_path=str(
                Path(Kilosort2Sorter.kilosort2_path).absolute()),
            output_folder=str(output_folder),
            channel_path=str(
                (output_folder / 'kilosort2_channelmap.m').absolute()),
            config_path=str((output_folder / 'kilosort2_config.m').absolute()),
        )

        kilosort2_config_txt = kilosort2_config_txt.format(
            nchan=recording.get_num_channels(),
            sample_rate=recording.get_sampling_frequency(),
            dat_file=str((output_folder / 'recording.dat').absolute()),
            projection_threshold=p['projection_threshold'],
            preclust_threshold=p['preclust_threshold'],
            minFR=p['minFR'],
            freq_min=p['freq_min'],
            sigmaMask=p['sigmaMask'],
            kilo_thresh=p['detect_threshold'],
            use_car=use_car,
            nPCs=p['nPCs']
        )

        kilosort2_channelmap_txt = kilosort2_channelmap_txt.format(
            nchan=recording.get_num_channels(),
            sample_rate=recording.get_sampling_frequency(),
            xcoords=[p[0] for p in positions],
            ycoords=[p[1] for p in positions],
            kcoords=groups
        )

        for fname, txt in zip(['kilosort2_master.m', 'kilosort2_config.m',
                               'kilosort2_channelmap.m'],
                              [kilosort2_master_txt, kilosort2_config_txt,
                               kilosort2_channelmap_txt]):
            with (output_folder / fname).open('w') as f:
                f.write(txt)

        shutil.copy(str(source_dir.parent / 'utils' / 'writeNPY.m'), str(output_folder))
        shutil.copy(str(source_dir.parent / 'utils' / 'constructNPYheader.m'), str(output_folder))

    def _run(self, recording, output_folder):
        if "win" in sys.platform:
            shell_cmd = '''
                        cd {tmpdir}
                        matlab -nosplash -nodisplay -wait -r kilosort2_master
                    '''.format(tmpdir=output_folder)
        else:
            shell_cmd = '''
                        #!/bin/bash
                        cd "{tmpdir}"
                        matlab -nosplash -nodisplay -r kilosort2_master
                    '''.format(tmpdir=output_folder)
        shell_cmd = ShellScript(shell_cmd, redirect_output_to_stdout=True)
        shell_cmd.start()

        retcode = shell_cmd.wait()

        if retcode != 0:
            raise Exception('kilosort2 returned a non-zero exit code')

    @staticmethod
    def get_result_from_folder(output_folder):
        sorting = se.KiloSortSortingExtractor(folder_path=output_folder)
        return sorting
