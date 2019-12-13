#!/bin/bash

HITHER_USE_SINGULARITY=TRUE ./main_analysis.py spec.json \
    -o testA.json \
    --test \
    --slurm slurm_config.json

