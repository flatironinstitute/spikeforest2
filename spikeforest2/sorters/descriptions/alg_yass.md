---
label: YASS
dockerfile: https://github.com/flatironinstitute/spikeforest/blob/master/spikeforest/spikesorters/yass/container/Dockerfile
environment: Python
wrapper: https://github.com/flatironinstitute/spikeforest/blob/master/spikeforest/spikesorters/yass/yass.py
website: https://yass.readthedocs.io/en/latest/
source_code: https://github.com/paninski-lab/yass
authors: Peter Lee, Eduardo Blancas, Nishchal Dethe, Shenghao Wu, Hooshmand Shokri, Calvin Tong, Catalin Mitelut, Liam Paninski
processor_name: Yass
doi: 10.1101/151928
---
_
# YASS

## Description

From the YASS bioRxiv paper [2]: This manuscript describes an efficient, reliable pipeline for spike sorting on dense multi-electrode arrays (MEAs), where neural signals appear across many electrodes and spike sorting currently represents a major computational bottleneck. We present several new techniques that make dense MEA spike sorting more robust and scalable. Our pipeline is based on an efficient multi-stage “triage-then-cluster-then-pursuit” approach that initially extracts only clean, high-quality waveforms from the electrophysiological time series by temporarily skipping noisy or “collided” events (representing two neurons firing synchronously). This is accomplished by developing a neural network detection method followed by efficient outlier triaging. The clean waveforms are then used to infer the set of neural spike waveform templates through nonparametric Bayesian clustering. Our clustering approach adapts a “coreset” approach for data reduction and uses efficient inference methods in a Dirichlet process mixture model framework to dramatically improve the scalability and reliability of the entire pipeline. The “triaged” waveforms are then finally recovered with matching-pursuit deconvolution techniques. The proposed methods improve on the state-of-the-art in terms of accuracy and stability on both real and biophysically-realistic simulated MEA data. Furthermore, the proposed pipeline is efficient, learning templates and clustering much faster than real-time for a ≃ 500-electrode dataset, using primarily a single CPU core.

Note: The YASS algorithm is not currently being tested on the SpikeForest site while the authors are working on releasing a newer version.

## References

[1] Lee, Jin Hyung, et al. "Yass: Yet another spike sorter." Advances in Neural Information Processing Systems. 2017.

[2] Paninski, Liam, and John Cunningham. "Neural data science: accelerating the experiment-analysis-theory cycle in large-scale neuroscience." bioRxiv (2017): 196949.
