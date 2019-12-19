#!/usr/bin/env python

from spikeforest2_utils import test_sort_tetrode
import hither

def main():
    # I force using singularity for kilosort2 because on my computer, when docker tries to use gpu it messes up nvidia-container-cli and I need to restart the computer
    import os
    os.environ['HITHER_USE_SINGULARITY'] = 'TRUE'
    jh = hither.SlurmJobHandler(
        working_dir='tmp_slurm',
        num_workers_per_batch=2,
        num_cores_per_job=2,
        use_slurm=True,
        additional_srun_opts=['-p gpu']
    )
    test_sort_tetrode(sorter_name='kilosort2', min_avg_accuracy=0.15, num_jobs=1, job_handler=jh)

if __name__ == '__main__':
    main()