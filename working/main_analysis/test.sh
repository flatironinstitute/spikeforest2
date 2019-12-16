#!/bin/bash

HITHER_USE_SINGULARITY=TRUE ./main_analysis.py spec2.json \
    -o testA.json \
    --cache default_readwrite \
    --slurm slurm_config2.json

