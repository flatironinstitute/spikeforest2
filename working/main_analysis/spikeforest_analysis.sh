#!/bin/bash

HITHER_USE_SINGULARITY=TRUE ./main_analysis.py spec.json \
    -o spikeforest_output1.json \
    --cache default_readwrite \
    --slurm slurm_config.json \
    --job-timeout 1200