# SpikeForest2 todo

## Recordings

* [DONE] spikeforest_recordings: Put objects at each study set and study

## Analysis

* Reproduce main analysis [IN PROGRESS]
    - Write main_analysis.py [IN PROGRESS]
    - Wrap remaining sorters
    - Expose parameters of sorters
    - Implement non-sorter processing
        - Summarize recording
        - Summarize sorting
        - Compare with ground truth
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