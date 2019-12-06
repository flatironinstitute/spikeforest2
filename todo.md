# SpikeForest2 todo

## Recordings

* [DONE] spikeforest_recordings: Put objects at each study set and study

## Analysis

* Reproduce main analysis [IN PROGRESS]
    - [PARTIAL-DONE] Write main_analysis.py
    - Wrap remaining sorters
    - Expose parameters of sorters
    - [DONE] Implement non-sorter processing
        - [DONE] Summarize recording
        - [DONE] Summarize sorting
        - [DONE] Compare with ground truth
    - Parallelize (hither)
    - Interface with slurm (hither)
* Improved timing reporting

## I/O

* AutoSortingExtractor: Specify output format of sorting.
    - For example, firings.mda, json
    - sf-sort: --output-format or -f argument

## Widgets

* View heatmap in Analysis widget
* View sorting result
* View comparison with ground truth
* sf-browse-recordings
    - Automatically get hash from spikeforest_recordings repo