#!/bin/bash

set -ex

# You must set the SPIKEFOREST_COMPUTE_RESOURCE_READWRITE_PASSWORD environment variable

exec ./run_compute_resource --database spikeforest_readwrite --compute-resource-id spikeforest1 --kachery default_readwrite