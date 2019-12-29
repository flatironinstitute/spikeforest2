#!/bin/bash

HITHER_USE_SINGULARITY=TRUE ./main_analysis.py \
    001c_spec.json \
    -o 001c_output.json \
    --cache default_readwrite \
    --slurm slurm_config.json \
    --job-timeout 3600 \
    --log-file 001c_log.txt
