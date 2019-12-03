import os
from typing import Any
import json
import fnmatch
import inspect
import shutil
from pathlib import Path
from copy import deepcopy
import kachery as ka
from ._temporarydirectory import TemporaryDirectory
from ._shellscript import ShellScript

def run_function_in_container(*,
        name: str, function,
        container: str,
        keyword_args: dict,
        input_file_keys: list,
        input_file_extensions: dict,
        output_file_keys: list,
        output_file_extensions: dict,
        additional_files: list=[],
        local_modules: list=[]
    ) -> Any:
    # generate source code
    with TemporaryDirectory(remove=True, prefix='tmp_hither_run_in_container_' + name) as temp_path:
        try:
            function_source_fname = os.path.abspath(inspect.getsourcefile(function))
        except:
            raise('Unable to get source file for function {}. Cannot run in a container.'.format(name))

        function_source_dirname = os.path.dirname(function_source_fname)
        function_source_basename = os.path.basename(function_source_fname)
        function_source_basename_noext = os.path.splitext(function_source_basename)[0]
        code = _read_python_code_of_directory(
            function_source_dirname,
            additional_files=additional_files,
            exclude_init=True
        )
        code['files'].append(dict(
            name='__init__.py',
            content='from .{} import {}'.format(
                function_source_basename_noext, name)
        ))
        hither_dir = os.path.dirname(os.path.realpath(__file__))
        kachery_dir = os.path.dirname(os.path.realpath(__file__))
        local_module_paths = []
        for lm in local_modules:
            if os.path.isabs(lm):
                local_module_paths.append(lm)
            else:
                local_module_paths.append(os.path.join(function_source_dirname, lm))
        code['dirs'].append(dict(
            name='_local_modules',
            content=dict(
                files=[],
                dirs=[
                    dict(
                        name=os.path.basename(local_module_path),
                        content=_read_python_code_of_directory(os.path.join(function_source_dirname, local_module_path), exclude_init=False)
                    )
                    for local_module_path in local_module_paths + [hither_dir]
                ]
            )
        ))

        _write_python_code_to_directory(os.path.join(temp_path, 'function_src'), code)

        keyword_args_adjusted = deepcopy(keyword_args)
        binds = dict()
        for iname in input_file_keys:
            if iname in keyword_args.keys():
                fname_outside = keyword_args[iname]
                if not _is_hash_url(fname_outside):
                    fname_inside = '/inputs/{}{}'.format(iname, input_file_extensions[iname])
                    keyword_args_adjusted[iname] = fname_inside
                    binds[fname_outside] = fname_inside
        outputs_tmp = os.path.join(temp_path, 'outputs')
        os.mkdir(outputs_tmp)
        binds[outputs_tmp] = '/outputs'
        outputs_to_copy = dict()
        for oname in output_file_keys:
            if oname in keyword_args.keys():
                fname_outside = keyword_args[oname]
                fname_inside = '/outputs/{}{}'.format(oname, output_file_extensions[oname])
                fname_temp = '{}/{}{}'.format(outputs_tmp, oname, output_file_extensions[oname])
                keyword_args_adjusted[oname] = fname_inside
                outputs_to_copy[fname_temp] = fname_outside

        run_py_script = """
            #!/usr/bin/env python

            from function_src import {function_name}
            import sys
            import json

            def main():
                _configure_kachery()
                kwargs = json.loads('{keyword_args_json}')
                retval = {function_name}(**kwargs)
                with open('/run_in_container/retval.json', 'w') as f:
                    json.dump(dict(retval=retval), f)
            
            def _configure_kachery():
                try:
                    import kachery as ka
                except:
                    return
                kachery_config = json.loads('{kachery_config_json}')
                ka.set_config(**kachery_config)

            if __name__ == "__main__":
                try:
                    main()
                except:
                    sys.stdout.flush()
                    sys.stderr.flush()
                    raise
        """.format(
            keyword_args_json=json.dumps(keyword_args_adjusted),
            kachery_config_json=json.dumps(ka.get_config()),
            function_name=name
        )

        # For unindenting
        ShellScript(run_py_script).write(os.path.join(temp_path, 'run.py'))

        env_vars_inside_container = dict(
            KACHERY_STORAGE_DIR='/kachery-storage',
            PYTHONPATH='/run_in_container/function_src/_local_modules',
            HOME='$HOME'
        )

        run_inside_script = """
            #!/bin/bash
            set -e

            {env_vars_inside_container} python3 /run_in_container/run.py
        """.format(
            env_vars_inside_container=' '.join(['{}={}'.format(k, v) for k, v in env_vars_inside_container.items()])
        )

        ShellScript(run_inside_script).write(os.path.join(temp_path, 'run.sh'))

        if not os.getenv('KACHERY_STORAGE_DIR'):
            raise Exception('You must set the environment variable: KACHERY_STORAGE_DIR')

        if os.getenv('HITHER_USE_SINGULARITY', None) == 'TRUE':
            run_outside_script = """
                #!/bin/bash

                singularity exec -e --contain \\
                    -B $KACHERY_STORAGE_DIR:/kachery-storage \\
                    -B {temp_path}:/run_in_container \\
                    -B /tmp:/tmp \\
                    -B $HOME:$HOME \\
                    {binds_str} \\
                    {container} \\
                    bash /run_in_container/run.sh
            """.format(
                binds_str=' '.join(['-B {}:{}'.format(a, b) for a, b in binds.items()]),
                container=container,
                temp_path=temp_path
            )
        else:
            run_outside_script = """
                #!/bin/bash

                docker run -it \\
                    --gpus all \\
                    -v /etc/passwd:/etc/passwd -u `id -u`:`id -g` \\
                    -v $KACHERY_STORAGE_DIR:/kachery-storage \\
                    -v {temp_path}:/run_in_container \\
                    -v /tmp:/tmp \\
                    -v $HOME:$HOME \\
                    {binds_str} \\
                    {container} \\
                    bash /run_in_container/run.sh
            """.format(
                binds_str=' '.join(['-v {}:{}'.format(a, b) for a, b in binds.items()]),
                container=_docker_form_of_container_string(container),
                temp_path=temp_path
            )

        ss = ShellScript(run_outside_script, keep_temp_files=False)
        ss.start()
        retcode = ss.wait()

        if retcode != 0:
            raise Exception('Non-zero exit code ({}) running {} in container {}'.format(retcode, name, container))

        with open(os.path.join(temp_path, 'retval.json')) as f:
            obj = json.load(f)
        retval = obj['retval']

        for a, b in outputs_to_copy.items():
            shutil.copyfile(a, b)

        return retval

def _docker_form_of_container_string(container):
    if container.startswith('docker://'):
        return container[len('docker://'):]
    else:
        return container

def _read_python_code_of_directory(dirname, exclude_init, additional_files=[]):
    patterns = ['*.py'] + additional_files
    files = []
    dirs = []
    for fname in os.listdir(dirname):
        if os.path.isfile(dirname + '/' + fname):
            matches = False
            for pattern in patterns:
                if fnmatch.fnmatch(fname, pattern):
                    matches = True
            if exclude_init and (fname == '__init__.py'):
                matches = False
            if matches:
                with open(dirname + '/' + fname) as f:
                    txt = f.read()
                files.append(dict(
                    name=fname,
                    content=txt
                ))
        elif os.path.isdir(dirname + '/' + fname):
            if (not fname.startswith('__')) and (not fname.startswith('.')):
                content = _read_python_code_of_directory(
                    dirname + '/' + fname, additional_files=additional_files, exclude_init=False)
                if len(content['files']) + len(content['dirs']) > 0:
                    dirs.append(dict(
                        name=fname,
                        content=content
                    ))
    return dict(
        files=files,
        dirs=dirs
    )

def _write_python_code_to_directory(dirname: str, code: dict) -> None:
    if os.path.exists(dirname):
        raise Exception(
            'Cannot write code to already existing directory: {}'.format(dirname))
    os.mkdir(dirname)
    for item in code['files']:
        fname0 = dirname + '/' + item['name']
        with open(fname0, 'w') as f:
            f.write(item['content'])
    for item in code['dirs']:
        _write_python_code_to_directory(
            dirname + '/' + item['name'], item['content'])

def _is_hash_url(path):
    algs = ['sha1', 'md5']
    for alg in algs:
        if path.startswith(alg + '://') or path.startswith(alg + 'dir://'):
            return True
    return False