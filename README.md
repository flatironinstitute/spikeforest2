# spikeforest2

SpikeForest -- spike sorting analysis for website -- version 2

## Installation

Because this project is under active and early-stage development, we provide instructions for installing the development version of SpikeForest2. This allows the software to be updated via `git pull && pip install -e .` in most cases.

Prerequisites: We have containerized the processing methods. Therefore, to run the spike sorters and other processing, you must have Docker >=19 (or Singularity >= 3.3) installed. These versions are needed in order to provide GPU support. If you would like to use singularity (rather than docker) then set the environment variable `HITHER_USE_SINGULARITY=TRUE`.

*Note*: It could be that kilosort2 inside singularity crashes when using singularity 3.3. The problem may be fixed in singularity 3.4.2, but further testing is required. It also seems that kilosort2 has trouble when more than one job is running on the same node on our cluster, even when it is running inside singularity containers. This probably has something to do with gpu conflicts (not sure).

Be sure to have Python >=3.6 as well as numpy installed.

Then, after cloning this repo:

```
cd spikeforest2
pip install -e .
```

See below for instructions on [installing spikeforest_widgets](#installing-spikeforest_widgets).

Hint: it is useful to operate in a conda environment or a virtualenv to avoid potential package conflicts.

## Recordings

The SpikeForest recordings (arranged into studies and study sets) may be found here: [spikeforest_recordings](https://github.com/flatironinstitute/spikeforest_recordings)

## Spike sorting wrappers

Python wrappers for the spike sorters, including the docker container definitions, are found in the [spikeforest2/sorters](spikeforest2/sorters) directory.

| Sorter  | Python wrapper | Dockerfile | Example | Tests |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| HerdingSpikes2  | [herdingspikes2](spikeforest2/sorters/herdingspikes2) | [Dockerfile](spikeforest2/sorters/herdingspikes2/container)  | | [tests](working/tests) |
| IronClust  | [ironclust](spikeforest2/sorters/ironclust) | [Dockerfile](spikeforest2/sorters/ironclust/container)  | | [tests](working/tests) |
| JRClust  | [not yet ported] | | | |
| Kilosort  | [kilosort](spikeforest2/sorters/kilosort) | [Dockerfile](spikeforest2/sorters/kilosort/container)  | | [tests](working/tests) |
| KiloSort2  | [kilosort2](spikeforest2/sorters/kilosort2) | [Dockerfile](spikeforest2/sorters/kilosort2/container)  | | [tests](working/tests) |
| Klusta  | [klusta](spikeforest2/sorters/klusta) | [Dockerfile](spikeforest2/sorters/klusta/container)  | | [tests](working/tests) |
| MountainSort4  | [mountainsort4](spikeforest2/sorters/mountainsort4) | [Dockerfile](spikeforest2/sorters/mountainsort4/container)  | | [tests](working/tests) |
| SpyKING CIRCUS  | [spykingcircus](spikeforest2/sorters/spykingcircus) | [Dockerfile](spikeforest2/sorters/spykingcircus/container)  | | [tests](working/tests) |
| Tridesclous  | [tridesclous](spikeforest2/sorters/tridesclous) | [Dockerfile](spikeforest2/sorters/tridesclous/container)  | | [tests](working/tests) |
| Waveclus  | [waveclus](spikeforest2/sorters/waveclus) | [Dockerfile](spikeforest2/sorters/waveclus/container)  | | [tests](working/tests) |

## SpikeForest widgets

Once you have spikeforest_widgets installed ([see below](#installing-spikeforest_widgets)), you may use the following commands to visualize recordings, sorting results, and full analyses:

```bash
sf-view-timeseries [path-to-recording]

sf-view-recording [path-to-recording]

sf-view-analysis [path-to-analysis]

# coming soon ...
sf-view-sorting --sorting [path] --recording [optional-path]
sf-view-comparison-with-truth --sorting [path] --sorting-true [path] --recording [optional-path]
```

For example:

```
sf-view-recording sha1://961f4a641af64dded4821610189f808f0192de4d/SYNTH_MEAREC_TETRODE/synth_mearec_tetrode_noise10_K10_C4/002_synth.json

sf-view-analysis sha1://3f0bdafedb3757dc3eddb9d3aeccd890830ac181/analysis.json
```

In addition to the desktop, it is also possible to view these widgets in Jupyter notebooks, colab notebooks, or on a website.

## Installing spikeforest_widgets

Prerequisites: Python >=3.6, NodeJS >=8

To use the spikeforest_widgets package for visualizing recordings, sorting results, and full analyses, you need to first install reactopya:

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
