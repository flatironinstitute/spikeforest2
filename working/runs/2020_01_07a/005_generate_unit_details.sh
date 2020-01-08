#!/bin/bash

./generate_unit_details.py output.json \
    --cache default_readwrite --slurm slurm_config.json \
    --log-file gud.log.txt \
    --studysets PAIRED_BOYDEN,PAIRED_CRCNS_HC1,PAIRED_KAMPFF,PAIRED_MEA64C_YGER
,PAIRED_MONOTRODE

