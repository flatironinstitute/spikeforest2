import kachery as ka
import spikeextractors as se
import numpy as np
from .mdaextractors import MdaSortingExtractor

class AutoSortingExtractor(se.SortingExtractor):
    def __init__(self, arg):
        super().__init__()
        self._hash = None
        if isinstance(arg, se.SortingExtractor):
            self._sorting = arg
            self.copy_unit_properties(sorting=self._sorting)
        else:
            self._sorting = None
            if 'kachery_config' in arg:
                ka.set_config(**arg['kachery_config'])
            if 'path' in arg:
                path = arg['path']
                if ka.get_file_info(path):
                    file_path = ka.load_file(path)
                    if not file_path:
                        raise Exception('Unable to realize file: {}'.format(path))
                    self._init_from_file(file_path, original_path=path, kwargs=arg)
                else:
                    raise Exception('Not a file: {}'.format(path))
            else:
                raise Exception('Unable to initialize sorting extractor')
    def _init_from_file(self, path: str, *, original_path: str, kwargs: dict):
        if original_path.endswith('.mda'):
            if 'paramsPath' in kwargs:
                params = ka.load_object(kwargs['paramsPath'])
                samplerate = params['samplerate']
            elif 'samplerate' in kwargs:
                samplerate = kwargs['samplerate']
            else:
                raise Exception('Missing argument: samplerate or paramsPath')
            self._sorting = MdaSortingExtractor(firings_file=path, samplerate=samplerate)
        else:
            raise Exception('Unsupported format for {}'.format(original_path))
        
    
    def hash(self):
        if not self._hash:
            if hasattr(self._sorting, 'hash'):
                if type(self._sorting.hash) == str:
                    self._hash = self._sorting.hash
                else:
                    self._hash = self._sorting.hash()
            else:
                self._hash = None
                # self._hash = _samplehash(self._sorting)
        return self._hash

    def get_unit_ids(self):
        return self._sorting.get_unit_ids()

    def get_unit_spike_train(self, **kwargs):
        return self._sorting.get_unit_spike_train(**kwargs)
    
    def get_sampling_frequency(self):
        return self._sorting.get_sampling_frequency()

class NwbSortingExtractor(se.SortingExtractor):
    def __init__(self, *, path, nwb_path):
        import h5py
        super().__init__()
        self._path = path
        with h5py.File(self._path, 'r') as f:
            X = load_nwb_item(file=f, nwb_path=nwb_path)
            self._spike_times = X['spike_times'][:] * self.get_sampling_frequency()
            self._spike_times_index = X['spike_times_index'][:]
            self._unit_ids = X['id'][:]
            self._index_by_id = dict()
            for index, id0 in enumerate(self._unit_ids):
                self._index_by_id[id0] = index

    def get_unit_ids(self):
        return [int(val) for val in self._unit_ids]

    def get_unit_spike_train(self, unit_id, start_frame=None, end_frame=None):
        if start_frame is None:
            start_frame = 0
        if end_frame is None:
            end_frame = np.Inf
        index = self._index_by_id[unit_id]
        ii2 = self._spike_times_index[index]
        if index - 1 >= 0:
            ii1 = self._spike_times_index[index - 1]
        else:
            ii1 = 0
        return self._spike_times[ii1:ii2]
    
    def get_sampling_frequency(self):
        # need to fix this
        return 30000

# def _samplehash(sorting):
#     from mountaintools import client as mt
#     obj = {
#         'unit_ids': sorting.get_unit_ids(),
#         'sampling_frequency': sorting.get_sampling_frequency(),
#         'data': _samplehash_helper(sorting)
#     }
#     return mt.sha1OfObject(obj)


# def _samplehash_helper(sorting):
#     h = 0
#     for id in sorting.get_unit_ids():
#         st = sorting.get_unit_spike_train(unit_id=id)
#         h = hash((hash(bytes(st)), hash(h)))
#     return h