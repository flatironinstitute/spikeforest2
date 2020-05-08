#!/usr/bin/env python

import os
import hither_sf as hither

@hither.function('hello_hither_scipy', '0.1.0')
@hither.container(default='docker://jupyter/scipy-notebook:latest')
def hello_hither_scipy(n=20):
    from scipy import linalg
    import numpy as np
    A = np.vander(np.arange(1, n+1))
    smallest_singular_value = np.min(linalg.svdvals(A))
    print(f'Hello, hither scipy: smallest singular value of Vandermonde matrix for x=[1..{n}] is {smallest_singular_value}')
    return smallest_singular_value

def example1():
    with hither.config(container='default'):
        result = hello_hither_scipy.run(n=20)
        print(result.retval)

def example1_parallel():
    results = []
    job_handler = hither.ParallelJobHandler(10)
    with hither.job_queue(), hither.config(container='default', job_handler=job_handler):
        for n in range(501, 511):
            result = hello_hither_scipy.run(n=n)
            setattr(result, 'n', n)
            results.append(result)
    for result in results:
        n = result.n
        elapsed_sec = result.runtime_info['elapsed_sec']
        retval = result.retval
        print(f'n={n}: result={retval}; elapsed(sec)={elapsed_sec}')

@hither.function('intentional_exception', '0.1.0')
@hither.container(default='docker://jupyter/scipy-notebook:latest')
def intentional_exception(raise_exception: bool):
    if raise_exception:
        raise Exception('Intentional exception')
    return 'value'

def example2():
    with hither.config(container='default'):
        result1 = intentional_exception.run(raise_exception=False)
        try:
            intentional_exception.run(raise_exception=True)
            got_exception = False
        except:
            got_exception = True
        assert got_exception, "Did not get exception"
        with hither.config(exception_on_fail=False):
            result3 = intentional_exception.run(raise_exception=True)
    assert result1.success, "result1.success should be True"
    assert (not result3.success), "result3.success should be False"
    print(result1.retval, result3.retval)

@hither.function('create_text_file', '0.1.0')
@hither.output_file('output_file')
def create_text_file(*, text: str, intentional_exception: bool, output_file: str):
    if intentional_exception:
        raise Exception('Intentional exception.')
    with open(output_file, 'w') as f:
        f.write(text)

@hither.function('print_file', '0.1.0')
@hither.input_file('input_file')
def print_file(*, input_file: str):
    with open(input_file, 'r') as f:
        print(f.read())

def example3():
    X = hither.File()
    create_text_file.run(text='some-text', intentional_exception=False, output_file=X)
    print_file.run(input_file=X)

    with hither.config(exception_on_fail=False):
        X2 = hither.File()
        create_text_file.run(text='some-text', intentional_exception=True, output_file=X2)
        result = print_file.run(input_file=X2)
        print(result.success)

def main():
    example3()

    with hither.config(container='docker://python:3.7'):
        example3()

    #example2()

    # with hither.config(cache='local', cache_failing=True):
    #     example2()

    # example1()

    # example1_parallel()

    # with hither.config(cache='local'):
    #     example1_parallel()

    # Test singularity
    # os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'
    # example1()
    # example1_parallel()

if __name__ == '__main__':
    main()