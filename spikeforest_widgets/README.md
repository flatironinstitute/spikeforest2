# spikeforest_widgets

A collection of [reactopya](https://github.com/flatironinstitute/reactopya) widgets for working with SpikeForest analyses.

## Installation

See [installation instructions](generated/docs/install.md).

## Usage

After you have properly installed this package with electron enabled:

```
import spikeforest_widgets as sw
sw.init_electron()

X = sw.Analysis(path='', download_from='spikeforest.public')
X.show()
```
