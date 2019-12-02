# spikeforest2

SpikeForest -- spike sorting analysis for website -- version 2

## Installation

After cloning this repo

```
cd spikeforest2
pip install -e .
```

## Recordings

The SpikeForest recordings (arranged into studies and study sets) may be found here: [spikeforest_recordings](https://github.com/flatironinstitute/spikeforest_recordings)

## Spike sorting wrappers

Python wrappers for the spike sorters, including the docker container definitions, are found in the [spikeforest2/sorters](spikeforest2/sorters) directory.

| Sorter  | Python wrapper | Dockerfile | Example |
| ------------- | ------------- | ------------- | ------------- |
| MountainSort4  | [mountainsort4](spikeforest2/sorters/mountainsort4) | [Dockerfile](spikeforest2/sorters/mountainsort4/container)  | [example_mountainsort4.py](examples/example_mountainsort4.py) |
| IronClust  | [ironclust](spikeforest2/sorters/ironclust) | [Dockerfile](spikeforest2/sorters/ironclust/container)  | [example_ironclust.py](examples/example_ironclust.py) |
| KiloSort2  | [kilosort2](spikeforest2/sorters/kilosort2) | [Dockerfile](spikeforest2/sorters/kilosort2/container)  | [example_kilosort2.py](examples/example_kilosort2.py) |
| SpyKING CIRCUS  | [spykingcircus](spikeforest2/sorters/spykingcircus) | [Dockerfile](spikeforest2/sorters/spykingcircus/container)  | [example_spykingcircus.py](examples/example_spykingcircus.py) |