#!/bin/bash

HITHER_USE_SINGULARITY=TRUE ./main_analysis.py \
    002_spec.json \
    -o 002_output.json \
    --cache default_readwrite \
    --slurm slurm_config.json \
    --job-timeout 1200