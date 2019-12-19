#!/bin/bash

HITHER_USE_SINGULARITY=TRUE ./main_analysis.py \
    001b_spec.json \
    -o 001b_output.json \
    --cache default_readwrite \
    --slurm slurm_config.json \
    --job-timeout 1200 \
    --log-file 001b_log.txt \
    --rerun-failing
