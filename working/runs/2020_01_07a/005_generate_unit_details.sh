#!/bin/bash

./generate_unit_details.py output.json \
    --cache default_readwrite --slurm slurm_config.json \
    --log-file gud.log.txt
