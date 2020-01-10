---
label: KILOSORT2
dockerfile:
environment: MATLAB
dockerfile: https://github.com/flatironinstitute/spikeforest2/blob/master/spikeforest2/sorters/kilosort2/container/Dockerfile
wrapper: https://github.com/flatironinstitute/spikeforest2/blob/master/spikeforest2/sorters/kilosort2/_kilosort2.py
website: https://github.com/MouseLand/Kilosort2
source_code: https://github.com/MouseLand/Kilosort2
authors: Marius Pachitariu
processor_name: KiloSort2
doi:
---
_
# KILOSORT2

## Description

*From the KiloSort2 website*: Kilosort2: automated spike sorting with drift tracking and template matching on GPUs

A Matlab package for spike sorting electrophysiological data up to 1024 channels. In many cases, and especially for Neuropixels probes, the automated output of Kilosort2 requires minimal manual curation.

## Installation notes

Requires CUDA toolkit to be installed

## References
