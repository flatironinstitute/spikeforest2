#!/bin/bash

HITHER_USE_SINGULARITY=TRUE ./main_analysis.py \
    001jrc_spec.json \
    -o 001jrc_output.json \
    --cache default_readwrite \
    --slurm slurm_config.json \
    --job-timeout 3600 \
    --log-file 001jrc_log.txt
