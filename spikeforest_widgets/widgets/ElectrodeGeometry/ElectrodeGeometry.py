import numpy as np
from mountaintools import client as mt
import spikeextractors as se

class ElectrodeGeometry:
    def __init__(self):
        super().__init__()

    def javascript_state_changed(self, prev_state, state):
        self.set_python_state(dict(status='running', status_message='Running'))
        mt.configDownloadFrom(state.get('download_from', []))
        path = state.get('path', None)
        if path:
            self.set_python_state(dict(status_message='Realizing file: {}'.format(path)))
            if path.endswith('.csv'):
                path2 = mt.realizeFile(path)
                if not path2:
                    self.set_python_state(dict(
                        status='error',
                        status_message='Unable to realize file: {}'.format(path)
                    ))
                    return
                self.set_python_state(dict(status_message='Loading locations'))
                x = np.genfromtxt(path2, delimiter=',')
                locations = x.T
                num_elec = x.shape[0]
                labels = ['{}'.format(a) for a in range(1, num_elec + 1)]
            else:
                raise Exception('Unexpected file type for {}'.format(path))
        else:
            locations = [[0, 0], [1, 0], [1, 1], [2, 1]]
            labels = ['1', '2', '3', '4']
        state = dict()
        state['locations'] = locations
        state['labels'] = labels
        state['status'] = 'finished'
        self.set_python_state(state)
