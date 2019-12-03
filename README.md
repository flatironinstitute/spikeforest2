# spikeforest2

SpikeForest -- spike sorting analysis for website -- version 2

## Installation

Prerequisites: you must have Docker >= 19 (or Singularity >= 3.3) installed. If you would like to use singularity (rather than docker) then set the environment variable `HITHER_USE_SINGULARITY=TRUE`.

After cloning this repo

```
cd spikeforest2
pip install -e .
```

See below for instructions on [installing spikeforest_widgets](#installing-spikeforest-widgets).

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

## SpikeForest widgets

Once you have spikeforest_widgets installed ([see below](#installing-spikeforest-widgets)), you may use the following commands to visualize recordings and sorting results:

```bash
sf-view-timeseries [path-to-recording]

sf-view-recording [path-to-recording]

# coming soon ...
sf-view-sorting --sorting [path] --recording [optional-path]
sf-view-comparison-with-truth --sorting [path] --sorting-true [path] --recording [optional-path]
```

For example:

```
sf-view-recording sha1://961f4a641af64dded4821610189f808f0192de4d/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.json
```

## Installing spikeForest widgets

Prerequisites: Python >=3.6, NodeJS >=8

To use the spikeforest_widgets package for visualizing recordings and sorting results, you need to first install reactopya:

```
pip install --upgrade reactopya
```

Then install the development version of spikeforest_widgets which is in a subdirectory of spikeforest2:

```
cd spikeforest_widgets
reactopya install
```

You will also need electron:

```
npm install -g electron
```

If you run into permissions problems, follow the instructions [here](https://github.com/sindresorhus/guides/blob/master/npm-global-without-sudo.md) to configure npm to install global packages inside your home directory.
