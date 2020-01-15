import kachery as ka
import hither
import os

def sort(algorithm: str, recording_path: str, sorting_out: str=None, container: str='default', git_annex_mode=True, use_singularity: bool=False)->str:
    
    from spikeforest2 import sorters
    # if not use_singularity:
    #     os.environ['HITHER_USE_SINGULARITY'] = 'FALSE'
    # else:        
    #     os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'
    print('HITHER_USE_SINGULARITY: ' + os.getenv('HITHER_USE_SINGULARITY'))
    if not hasattr(sorters, algorithm):
        raise Exception('Sorter not found: {}'.format(algorithm))
    sorter = getattr(sorters, algorithm)
    if algorithm in ['kilosort2', 'kilosort', 'ironclust', 'tridesclous']:
        gpu = True
    else:
        gpu = False
    if not sorting_out:
        sorting_out = hither.File()
    if not recording_path.startswith('sha1dir://') or not recording_path.startswith('sha1://'):
        if os.path.isfile(recording_path):
            recording_path = ka.store_file(recording_path)
        elif os.path.isdir(recording_path):
            recording_path = ka.store_dir(recording_path, git_annex_mode = git_annex_mode)        
    with hither.config(gpu=gpu, container=container):
        result = sorter.run(recording_path=recording_path, sorting_out=sorting_out)
    print('SORTING')
    print('==============================================')
    return ka.store_file(result.outputs.sorting_out._path, basename='firings.mda')