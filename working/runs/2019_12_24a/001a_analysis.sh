#!/bin/bash

HITHER_USE_SINGULARITY=TRUE ./main_analysis.py \
    001a_spec.json \
    -o 001a_output.json \
    --cache default_readwrite \
    --slurm slurm_config.json \
    --job-timeout 3600 \
    --log-file 001a_log.txt
