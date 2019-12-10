import shutil
import json
import os
import random
# import tempfile
import time
from typing import Union, Any, Dict
from copy import deepcopy
from ._etconf import ETConf

from spikeforest2_utils import ConsoleCapture
from ._run_function_in_container import run_function_in_container, _serialize_runnable_function

_global_config = ETConf(
    defaults=dict(
        container=None,
        cache=None,
        force_run=None,
        gpu=None,
        job_handler=None
    )
)

_global: Dict[str, Union[list, bool]] = dict(
    pending_jobs=[], # waiting for inputs to be ready - not yet sent to job handler
    queued_jobs=[], # inputs are ready, sent to job handler
    inside_job_queue=False
)

class config:
    def __init__(self,
        container: Union[str, None]=None,
        cache: Union[str, dict, None]=None,
        force_run: Union[bool, None]=None,
        gpu: Union[bool, None]=None,
        job_handler: Union[Any, None]=None
    ):
        self._config = dict(
            container=container,
            cache=cache,
            force_run=force_run,
            gpu=gpu,
            job_handler=job_handler
        )
        self._old_config = None
    def __enter__(self):
        self._old_config = get_config()
        set_config(**self._config)
    def __exit__(self, exc_type, exc_val, exc_tb):
        set_config(**self._old_config)

class job_queue:
    def __init__(self):
        pass
    def __enter__(self):
        if _global['inside_job_queue']:
            raise Exception('Cannot be in more than one hither job queue')
        _global['inside_job_queue'] = True
    def __exit__(self, exc_type, exc_val, exc_tb):
        wait()
        _global['inside_job_queue'] = False

def set_config(
        container: Union[str, None]=None,
        cache: Union[str, dict, None]=None,
        force_run: Union[bool, None]=None,
        gpu: Union[bool, None]=None,
        job_handler: Union[Any, None]=None
) -> None:
    _global_config.set_config(container=container, cache=cache, force_run=force_run, gpu=gpu, job_handler=job_handler)

def get_config() -> dict:
    return _global_config.get_config()

def function(name, version):
    def wrap(f):
        def run(**kwargs):
            import kachery as ka

            config = _global_config.get_config()
            _container = config['container']
            _cache = config['cache']
            _force_run = config['force_run']
            _gpu = config['gpu']
            _job_handler = config['job_handler']
            hash_object: Dict[Union[str, Dict[Any]]] = dict(
                api_version='0.1.0',
                name=name,
                version=version,
                input_files=dict(), # to be determined later
                output_files=dict(),
                parameters=dict()
            )
            used_kwargs = dict()
            hither_input_files = getattr(f, '_hither_input_files', [])
            hither_output_files = getattr(f, '_hither_output_files', [])
            hither_parameters = getattr(f, '_hither_parameters', [])

            # Let's make sure the input and output files are all coming in as File objects
            for input_file in hither_input_files:
                iname = input_file['name']
                if iname in kwargs:
                    if type(kwargs[iname]) == str:
                        kwargs[iname] = File(kwargs[iname])
            for output_file in hither_output_files:
                oname = output_file['name']
                if oname in kwargs:
                    if type(kwargs[oname]) == str:
                        kwargs[oname] = File(kwargs[oname])

            for input_file in hither_input_files:
                iname = input_file['name']
                if iname not in kwargs or kwargs[iname] is None:
                    if input_file['required']:
                        raise Exception('Missing required input file: "{}"'.format(iname))
                else:
                    x = kwargs[iname]
                    hash_object['input_files'][iname] = x # later we resolve this
                    used_kwargs[iname] = True
            
            output_file_keys = []
            for output_file in hither_output_files:
                oname = output_file['name']
                if oname not in kwargs or kwargs[oname] is None:
                    if output_file['required']:
                        raise Exception('Missing required output file: {}'.format(oname))
                else:
                    x = kwargs[oname]
                    x2 = x._path
                    if _is_hash_url(x2):
                        raise Exception('Output file {} cannot be a hash URI: {}'.format(oname, x2))
                    used_kwargs[oname] = True
                    output_file_keys.append(oname)

            for parameter in hither_parameters:
                pname = parameter['name']
                val = None
                if pname not in kwargs or kwargs[pname] is None:
                    if parameter['required']:
                        raise Exception('Missing required parameter: {}'.format(pname))
                    if 'default' in parameter:
                        used_kwargs[pname] = True
                        val = parameter['default']
                else:
                    used_kwargs[pname] = True
                    val = kwargs[pname]
                hash_object['parameters'][pname] = val

            for k, v in kwargs.items():
                if k not in used_kwargs:
                    hash_object['parameters'][k] = v
                    used_kwargs[k] = True
            
            result = Result()
            result.outputs = Outputs()
            for oname in output_file_keys:
                setattr(result.outputs, oname, kwargs[oname])
                result._output_names.append(oname)
            result.runtime_info = None
            result.version = version
            result.hash_object = hash_object
            result.retval = None
            result.container = _container

            job = dict(
                name=name,
                version=version,
                f=f,
                kwargs=kwargs,
                hash_object=hash_object,
                result=result,
                container = _container,
                cache = _cache,
                force_run = _force_run,
                gpu = _gpu,
                job_handler = _job_handler,
                status='pending'
            )
            if _global['inside_job_queue'] and job['job_handler'] is not None:
                _global['pending_jobs'].append(job)
            else:
                if job['job_handler'] is not None:
                    raise Exception('Cannot use job handler without a job queue')
                if not _job_is_ready(job):
                    if not _global['inside_job_queue']:
                        raise Exception(f'Job {name} is not ready and you are not inside a job queue.')
                    else:
                        raise Exception(f'Job {name} is not ready and you are not using a job handler.')
                _prepare_job_to_run(job)
                if not _check_cache_for_job_result(job):
                    _run_job(job)
                    job['status'] = 'finished'
                    result = job['result']
                    _handle_temporary_outputs([getattr(result.outputs, oname) for oname in result._output_names])
                    if job['cache'] is not None:
                        _store_result(serialized_result=_internal_serialize_result(job['result']), cache=job['cache'])
            return job['result']
        setattr(f, 'run', run)
        return f
    return wrap

def _job_is_ready(job):
    for f in job['hash_object']['input_files'].values():
        if not f._exists:
            return False
    return True

def _prepare_job_to_run(job):
    import kachery as ka
    
    name = job['name']
    # version = job['version']
    f = job['f']
    kwargs = job['kwargs']

    _container = job['container']
    _cache = job['cache']
    # _force_run = job['force_run']
    _gpu = job['gpu']
    _job_handler = job['job_handler']
    hash_object = job['hash_object']
    result = job['result']
    resolved_input_files = dict()
    hither_input_files = getattr(f, '_hither_input_files', [])
    hither_output_files = getattr(f, '_hither_output_files', [])
    # hither_parameters = getattr(f, '_hither_parameters', [])

    input_file_keys = []
    input_file_extensions = dict()
    for input_file in hither_input_files:
        iname = input_file['name']
        if iname not in kwargs or kwargs[iname] is None:
            if input_file['required']:
                raise Exception('Unexpected: missing required input file: "{}"'.format(iname))
        else:
            x = kwargs[iname]
            # a hither File object
            if x._path is None:
                raise Exception('Unexpected: input file has no path: {}'.format(iname))
            # we really want the path
            x2 = x._path
            if _is_hash_url(x2) and input_file['kachery_resolve']:
                # a hash url
                y = ka.load_file(x2)
                if y is None:
                    raise Exception('Unable to load input file {}: {}'.format(iname, x))
                x2 = y
            info0 = ka.get_file_info(x2)
            if info0 is None:
                raise Exception('Unable to get info for input file {}: {}'.format(iname, x2))
            tmp0 = dict()
            for field0 in ['sha1', 'md5']:
                if field0 in info0:
                    tmp0[field0] = info0[field0]
            hash_object['input_files'][iname] = tmp0
            input_file_keys.append(iname)
            input_file_extensions[iname] = _file_extension(x._path)
            resolved_input_files[iname] = x2
    
    resolved_output_files = dict()
    output_file_keys = []
    output_file_extensions = dict()
    for output_file in hither_output_files:
        oname = output_file['name']
        if oname not in kwargs or kwargs[oname] is None:
            if output_file['required']:
                raise Exception('Unexpected: missing required output file: {}'.format(oname))
        else:
            x = kwargs[oname]
            x2 = x._path
            if _is_hash_url(x2):
                raise Exception('Output file {} cannot be a hash URI: {}'.format(oname, x2))
            resolved_output_files[oname] = x2
            output_file_keys.append(oname)
            output_file_extensions[oname] = _file_extension(x._path)

    resolved_parameters = hash_object['parameters']

    resolved_kwargs = dict()
    for k, v in resolved_input_files.items():
        resolved_kwargs[k] = v
    for k, v in resolved_output_files.items():
        resolved_kwargs[k] = v
    for k, v in resolved_parameters.items():
        resolved_kwargs[k] = v

    job['resolved_kwargs'] = resolved_kwargs
    job['input_file_keys'] = input_file_keys
    job['input_file_extensions'] = input_file_extensions
    job['output_file_keys'] = output_file_keys
    job['output_file_extensions'] = output_file_extensions

def _run_job(job):
    resolved_kwargs = job['resolved_kwargs']
    name = job['name']
    f = job.get('f', None)
    f_serialized = job.get('f_serialized', None)
    _container = job['container']
    _gpu = job['gpu']
    _cache = job['cache']
    input_file_keys = job['input_file_keys']
    input_file_extensions = job['input_file_extensions']
    output_file_keys = job['output_file_keys']
    output_file_extensions = job['output_file_extensions']
    result = job['result']

    if _container is None and f is not None:
        with ConsoleCapture(name) as cc:
            returnval = f(**resolved_kwargs)
        runtime_info = cc.runtime_info()
    else:
        with ConsoleCapture(name) as cc:
            if f is not None:
                local_modules = getattr(f, '_hither_local_modules', [])
            else:
                local_modules = []
            print('===== Hither: running {} in container: {}'.format(name, _container))
            returnval, runtime_info = run_function_in_container(
                name=name,
                function=f,
                function_serialized = f_serialized,
                input_file_keys=input_file_keys,
                input_file_extensions=input_file_extensions,
                output_file_keys=output_file_keys,
                output_file_extensions=output_file_extensions,
                container=_container,
                keyword_args=resolved_kwargs,
                local_modules=local_modules,
                gpu=_gpu
            )
        runtime_info['container_runtime_info'] = cc.runtime_info()
    
    result.retval = returnval
    result.runtime_info = runtime_info

    job['status'] = 'finished'

def wait(timeout: Union[float, None]=None):
    timer = time.time()
    while True:
        pending_jobs = _global['pending_jobs']
        queued_jobs = _global['queued_jobs']
        if len(pending_jobs) == 0 and len(queued_jobs) == 0:
            break
        new_pending_jobs = []
        active_job_handlers = []
        for job in pending_jobs:
            active_job_handlers.append(job['job_handler'])
            if job['status'] == 'pending':
                if _job_is_ready(job):
                    _prepare_job_to_run(job)
                    if not _check_cache_for_job_result(job):
                        job['status'] = 'queued'
                        queued_jobs.append(job)
                        job_handler = job['job_handler']
                        
                        if job_handler:
                            job_handler.handle_job(job)
                        else:
                            _run_job(job)
                            if job['cache'] is not None:
                                _store_result(serialized_result=_internal_serialize_result(job['result']), cache=job['cache'])
                else:
                    new_pending_jobs.append(job)
        _global['pending_jobs'] = new_pending_jobs

        new_queued_jobs = []
        for job in queued_jobs:
            active_job_handlers.append(job['job_handler'])
            if job['status'] == 'queued':
                new_queued_jobs.append(job)
            elif job['status'] == 'finished':
                if job['cache'] is not None:
                    _store_result(serialized_result=_internal_serialize_result(job['result']), cache=job['cache'])
        _global['queued_jobs'] = new_queued_jobs

        elapsed = time.time() - timer
        if timeout is not None:
            if elapsed > timeout:
                return
        
        # iterate the job handlers
        unique_active_job_handlers = []
        for h in active_job_handlers:
            found = False
            for h2 in unique_active_job_handlers:
                if h is h2:
                    found = True
            if not found:
                unique_active_job_handlers.append(h)
        for h in unique_active_job_handlers:
            h.iterate()

        time.sleep(0.5)

def _console_out_to_str(console_out):
    txt = ''
    for console_line in console_out['lines']:
        txt = txt + '{} {}: {}\n'.format(console_out.get('label', ''), _fmt_time(console_line['timestamp']), console_line['text'])
    return txt

def _fmt_time(t):
    import datetime
    return datetime.datetime.fromtimestamp(t).isoformat()

def _handle_temporary_outputs(outputs):
    import kachery as ka
    for output in outputs:
        if not output._exists:
            old_path = output._path
            new_path = ka.load_file(ka.store_file(old_path))
            output._path = new_path
            output._is_temporary = False
            output._exists = True
            os.unlink(old_path)

def input_file(name: str, required=True, kachery_resolve=True):
    def wrap(f):
        hither_input_files = getattr(f, '_hither_input_files', [])
        hither_input_files.append(dict(
            name=name,
            required=required,
            kachery_resolve=kachery_resolve
        ))
        setattr(f, '_hither_input_files', hither_input_files)
        return f
    return wrap

def output_file(name: str, required=True):
    def wrap(f):
        hither_output_files = getattr(f, '_hither_output_files', [])
        hither_output_files.append(dict(
            name=name,
            required=required
        ))
        setattr(f, '_hither_output_files', hither_output_files)
        return f
    return wrap

def container(**kwargs):
    def wrap(f):
        if not hasattr(f, '_hither_containers'):
            setattr(f, '_hither_containers', dict())
        containers = getattr(f, '_hither_containers')
        for k, v in kwargs.items():
            containers[k] = v
        return f
    return wrap

def local_module(module_path):
    def wrap(f):
        if not hasattr(f, '_hither_local_modules'):
            setattr(f, '_hither_local_modules', [])
        getattr(f, '_hither_local_modules').append(module_path)
        return f
    return wrap

def parameter(name: str, required=True, default=None):
    def wrap(f):
        hither_parameters = getattr(f, '_hither_parameters', [])
        hither_parameters.append(dict(
            name=name,
            required=required,
            default=default
        ))
        setattr(f, '_hither_parameters', hither_parameters)
        return f
    return wrap

def _check_cache_for_job_result(job):
    _cache = job['cache']
    _force_run = job['force_run']
    if _cache is None or _force_run:
        return False
    result0 = _load_result(hash_object=job['hash_object'], cache=job['cache'])
    if result0 is None:
        return False
    result0 = _internal_deserialize_result(result0)
    if result0 is None:
        return False
    print('===== Hither: found result of {} in cache'.format(job['name']))
    result = job['result']
    _set_result(job, result0)
    console_out_str = _console_out_to_str(result.runtime_info['console_out'])
    print(console_out_str)
    return True

def _set_result(job, result):
    result1 = job['result']
    result2 = result
    result1.runtime_info = result2.runtime_info
    result1.container = result2.container
    result1.retval = result2.retval
    result1.status = result2.status
    _handle_temporary_outputs([getattr(result2.outputs, oname) for oname in result2._output_names])
    for oname in result2._output_names:
        output1 = getattr(result1.outputs, oname)
        output2 = getattr(result2.outputs, oname)
        output1._path = output2._path
        output1._exists = output2._exists
        output1._is_temporary = output2._is_temporary
        
        setattr(result1.outputs, oname, getattr(result2.outputs, oname))
    job['status'] = 'finished'

def _load_result(*, hash_object, cache):
    import kachery as ka
    import loggery
    if type(cache) == str:
        cache = dict(preset=cache)
    with loggery.config(**cache):
        name0 = 'hither_result'
        hash0 = ka.get_object_hash(hash_object)
        doc = loggery.find_one({'message.name': name0, 'message.hash': hash0})
        if doc is None:
            return None
        return doc['message']

def _store_result(*, serialized_result, cache):
    import loggery
    if type(cache) == str:
        cache = dict(preset=cache)
    with loggery.config(**cache):
        loggery.insert_one(message=serialized_result)

class Result():
    def __init__(self):
        self.version = None
        self.container = None
        self.hash_object = None
        self.runtime_info = None
        self.retval = None
        self.status = None
        self.outputs = Outputs()
        self._output_names = []
        self._keys = ['version', 'container', 'hash_object', 'runtime_info', 'retval', 'status', '_output_names']
    def serialize(self):
        ret = dict()
        for k in self._keys:
            ret[k] = getattr(self, k)
        ret['outputs'] = dict()
        for oname in self._output_names:
            ret['outputs'][oname] = getattr(self.outputs, oname).serialize()
        return ret
    def deserialize(self, obj):
        for k in self._keys:
            setattr(self, k, obj[k])
        for oname in self._output_names:
            ff = File()
            ff.deserialize(obj['outputs'][oname])
            setattr(self.outputs, oname, ff)

# This is confusing -- it is a different type of serialization than result.serialize()!
def _internal_serialize_result(result):
    import kachery as ka
    ret: Dict[Any] = dict(
        output_files=dict()
    )
    ret['name'] = 'hither_result'

    ret['runtime_info'] = deepcopy(result.runtime_info)
    ret['runtime_info']['console_out'] = ka.store_object(ret['runtime_info'].get('console_out', ''))

    for oname in result._output_names:
        path = getattr(result.outputs, oname)._path
        ret['output_files'][oname] = ka.store_file(path)

    ret['retval'] = result.retval
    ret['version'] = result.version
    ret['container'] = result.container
    ret['hash_object'] = result.hash_object
    ret['hash'] = ka.get_object_hash(result.hash_object)
    ret['status'] = result.status
    return ret

# This is confusing -- it is a different type of deserialization than result.deserialize()!
def _internal_deserialize_result(obj):
    import kachery as ka
    result = Result()
    
    result.runtime_info = obj['runtime_info']
    result.runtime_info['console_out'] = ka.load_object(result.runtime_info.get('console_out', ''))
    if result.runtime_info['console_out'] is None:
        return None
    
    output_files = obj['output_files']
    for oname, path in output_files.items():
        path2 = ka.load_file(path)
        if path2 is None:
            print('Unable to find file when deserializing result.')
            return None
        setattr(result.outputs, oname, File(path2))
        result._output_names.append(oname)
    
    result.retval = obj['retval']
    result.version = obj.get('version', None)
    result.container = obj.get('container', None)
    result.hash_object = obj['hash_object']
    result.status = obj['status']
    return result

def _serialize_runnable_job(job):
    job_serialized = dict()
    for k,v in job.items():
        if k not in ['result', 'job_handler', 'f']:
            job_serialized[k] = _smartcopy(v)
    if 'f' in job:
        local_modules = getattr(job['f'], '_hither_local_modules', [])
        job_serialized['f_serialized'] = _serialize_runnable_function(
            job['f'],
            name=job['name'],
            additional_files=[], # fix this in the future
            local_modules=local_modules,
            container=job['container']
        )
    job_serialized['result'] = job['result'].serialize()
    return job_serialized

def _deserialize_runnable_job(job_serialized):
    job = dict()
    for k,v in job_serialized.items():
        if k not in ['result']:
            job[k] = _smartcopy(v)
    job['result'] = Result()
    job['result'].deserialize(job_serialized['result'])
    return job

def _smartcopy(v):
    if isinstance(v, dict):
        if '_hither_type' in v:
            if v['_hither_type'] == 'File':
                f = File()
                f.deserialize(v)
                return f
            else:
                raise Exception('Unexpected hither type: {}'.format(v['_hither_type']))
        ret = dict()        
        for k1, v1 in v.items():
            ret[k1] = _smartcopy(v1)
        return ret
    elif isinstance(v, list):
        ret = []
        for v1 in v:
            ret.append(_smartcopy(v1))
        return ret
    elif isinstance(v, File):
        ret = v.serialize()
        return ret
    else:
        try:
            json.dumps(v)
        except:
            raise Exception('Value is not json serializable')
        return deepcopy(v)   

class Outputs():
    def __init__(self):
        pass


class File():
    def __init__(self, path: Union[str, None]=None):
        if path is None:
            self._exists = False
            self._is_temporary = True
            path = _make_temporary_file('hither_temporary_file_')
        else:
            self._exists = True
            self._is_temporary = False
        self._path = path
    def __str__(self):
        if self._path is not None:
            return 'hither.File({})'.format(self._path)
        else:
            return 'hither.File()'
    def serialize(self):
        return dict(
            _hither_type='File',
            _exists=self._exists,
            _is_temporary=self._is_temporary,
            _path=self._path
        )
    def deserialize(self, obj):
        self._path = obj['_path']
        self._exists = obj['_exists']
        self._is_temporary = obj['_is_temporary']

def _is_hash_url(path):
    algs = ['sha1', 'md5']
    for alg in algs:
        if path.startswith(alg + '://') or path.startswith(alg + 'dir://'):
            return True
    return False

def _make_temporary_file(prefix):
    storage_dir = os.environ.get('KACHERY_STORAGE_DIR', None)
    if storage_dir is None:
        storage_dir = '/tmp'
    else:
        storage_dir = os.path.join(storage_dir, 'tmp')
        if not os.path.exists(storage_dir):
            os.mkdir(storage_dir)
    return os.path.join(storage_dir, 'hither_tmp_{}_{}'.format(prefix, _random_string(8)))

def _file_extension(x):
    _, ext = os.path.splitext(x)
    return ext

def _random_string(num: int):
    """Generate random string of a given length.
    """
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=num))