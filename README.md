# SpikeForest (v2)

This project contains the processing pipelines needed to reproduce the benchmarking results presented on the [spikeforest website](https://spikeforest.flatironinstitute.org).

Our bioRxiv preprint: [SpikeForest: reproducible web-facing ground-truth validation of automated neural spike sorters](https://www.biorxiv.org/content/10.1101/2020.01.14.900688v1)

High-level scripts used to generate the website results may be found in the [working/runs](working/runs) directory.

See below for information about the spike sorter wrappers and ground truth recordings.

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

Set the KACHERY_STORAGE_DIR environment variable to point to a path on your local machine where temporary files will be stored.

Optional: See below for instructions on [installing spikeforest_widgets](#installing-spikeforest_widgets).

Hint: It is useful to operate in a conda environment or a virtualenv to avoid potential package conflicts.

## Recordings

The SpikeForest recordings (arranged into studies and study sets) may be found here: [spikeforest_recordings](https://github.com/flatironinstitute/spikeforest_recordings).
Instructions on accessing these recordings using SpikeInterface Python objects are found below.

## Spike sorting wrappers

Python wrappers for the spike sorters, including the docker container definitions, are found in the [spikeforest2/sorters](spikeforest2/sorters) directory.

| Sorter  | Python wrapper | Dockerfile | Example | Tests |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| HerdingSpikes2  | [herdingspikes2](spikeforest2/sorters/herdingspikes2) | [Dockerfile](spikeforest2/sorters/herdingspikes2/container)  | | [tests](working/tests) |
| IronClust  | [ironclust](spikeforest2/sorters/ironclust) | [Dockerfile](spikeforest2/sorters/ironclust/container)  | | [tests](working/tests) |
| JRClust  | [ironclust](spikeforest2/sorters/jrclust) | [Dockerfile](spikeforest2/sorters/jrclust/container)  | | [tests](working/tests) |
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

## Accessing data via Python API

You can use [SpikeInterface](https://github.com/SpikeInterface) objects to access SpikeForest data from Python scripts. For example:

```python
from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor
import kachery as ka

# Configure kachery to download data from the public database
ka.set_config(fr='default_readonly')

# Specify the recording and ground truth sorting
recording_path = 'sha1://ee5214337b2e01910a92c3613a4b8ad4be4dc476/SYNTH_MAGLAND/synth_magland_noise10_K10_C4/001_synth.json'
sorting_true_path = 'sha1://ff64f1713227c017052bf21b41ddf764320aa606/SYNTH_MAGLAND/synth_magland_noise10_K10_C4/001_synth.firings_true.json'

recording = AutoRecordingExtractor(recording_path, download=False)
sorting_true = AutoSortingExtractor(sorting_true_path)

# Now you can access the recording using the SpikeInterface API
# For example, print the electrode locations and unit IDs
print(recording.get_channel_locations())
print(sorting_true.get_unit_ids())
```

The sha1:// reference strings may be obtained from the self_reference field in the .json files in the [spikeforest_recordings](https://github.com/flatironinstitute/spikeforest_recordings) repository.

If you are only interested in accessing small parts of the recording, use `download=False` as above. Otherwise, to download the entire recording to your local machine, use `download=True`.

It is also possible to use information from the SpikeForest website rather than from the spikeforest_recordings repository to specify the recording and sorting of interest. For example, the following data was obtained from the website:

```python
recording_path = 'sha1dir://fb52d510d2543634e247e0d2d1d4390be9ed9e20.synth_magland/datasets_noise10_K10_C4/010_synth'
sorting_true_path = 'sha1dir://fb52d510d2543634e247e0d2d1d4390be9ed9e20.synth_magland/datasets_noise10_K10_C4/010_synth/firings_true.mda'
```

This is just a different way of referencing the same information.
