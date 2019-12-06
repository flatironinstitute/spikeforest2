---
label: KLUSTA
dockerfile: https://github.com/flatironinstitute/spikeforest/blob/master/spikeforest/spikesorters/klusta/container/Dockerfile
wrapper: https://github.com/flatironinstitute/spikeforest/blob/master/spikeforest/spikesorters/klusta/klusta.py
notes: It uses Masked KlustaKwik for automated clustering
website: https://github.com/kwikteam/klusta
source_code: https://github.com/kwikteam/klusta
authors: Cyrille Rossant, Shabnam Kadir, Dan Goodman, Max Hunter, and Kenneth Harris
processor_name: Klusta
doi: 10.1038/nn.4268
---
_
# KLUSTA

## Description
*From the Klusta website*: Klusta: automatic spike sorting up to 64 channel. 

[**klusta**]
(https://github.com/kwikteam/klusta) is an open source package for automatic spike sorting of multielectrode neurophysiological recordings made with probes containing up to a few dozens of sites.

**klusta** implements the following features:

* **Kwik**: An HDF5-based file format that stores the results of a spike sorting session.
* **Spike detection** (also known as SpikeDetekt): an algorithm designed for probes containing tens of channels, based on a flood-fill algorithm in the adjacency graph formed by the recording sites in the probe.
* **Automatic clustering** (also known as Masked KlustaKwik): an automatic clustering algorithm designed for high-dimensional structured datasets.



## References
[1] Rossant, Cyrille, et al. (2016). Spike sorting for large, dense electrode arrays. Nature Neuroscience, 19, 634–641.
[2] Kadir, S.N., Goodman, D.F. & Harris, K.D. (2014). High-dimensional cluster analysis with the masked EM algorithm. Neural Comput. 26, 2379–2394.