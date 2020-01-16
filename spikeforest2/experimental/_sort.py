import kachery as ka
import hither
import os

def sort(algorithm: str, recording_path: str, sorting_out: str=None, 
    params: dict=None, container: str='default', git_annex_mode=True, 
    use_singularity: bool=False, job_timeout: float=3600
)->str:
    
    from spikeforest2 import sorters
    HITHER_USE_SINGULARITY = os.getenv('HITHER_USE_SINGULARITY')
    if HITHER_USE_SINGULARITY is None:
        HITHER_USE_SINGULARITY = False
    print('HITHER_USE_SINGULARITY: ' + HITHER_USE_SINGULARITY)
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
    params_hither = dict(gpu=gpu, container=container)    
    if job_timeout is not None:
        params_hither["job_timeout"] = job_timeout
    with hither.config(**params_hither):
        if params is None:        
            result = sorter.run(recording_path=recording_path, sorting_out=sorting_out)
        else:
            result = sorter.run(recording_path=recording_path, sorting_out=sorting_out, **params)
    print('SORTING')
    print('==============================================')
    return ka.store_file(result.outputs.sorting_out._path, basename='firings.mda')


# def set_params(sorter, params_file):
#     params = {}
#     names_float = ['detection_thresh']
#     with open(params_file, 'r') as myfile:
#         for line in myfile:
#             name, var = line.partition("=")[::2]
#             name = name.strip()

#             params[name.strip()] = var
#     sorter.set_params(**params)