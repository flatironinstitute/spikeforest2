#!/bin/bash

HITHER_USE_SINGULARITY=TRUE ./main_analysis.py \
    001_irc_boyden_spec.json \
    -o 001_irc_boyden_output.json \
    --cache default_readwrite \
    --slurm slurm_config.json \
    --job-timeout 3600 \
    --force-run \
    --log-file 001_irc_boyden_log.txt
