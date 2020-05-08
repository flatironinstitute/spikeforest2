#!/usr/bin/env python

import numpy as np
import spikeextractors as se
from spikeforest2 import processing
import hither_sf as hither

def main():
    samplerate = 30000
    duration_sec = 10 # number of timepoints
    true_firing_rates_hz = [1, 2, 3, 4, 5]
    approx_false_negative_rates = [0, 0.1, 0.2, 0.3, 0.4]
    approx_false_positive_rates = [0, 0.2, 0.1, 0.4, 0.3]
    extra_unit_firing_rates_hz = [0.5, 1, 1.5]

    num_timepoints = samplerate * duration_sec

    sorting_true = se.NumpySortingExtractor()
    sorting = se.NumpySortingExtractor()
    for ii in range(len(true_firing_rates_hz)):
        num_events = int(duration_sec * true_firing_rates_hz[ii])
        times0 = np.random.choice(np.arange(num_timepoints), size=num_events, replace=False).astype(float)
        num_hits = int((1 - approx_false_negative_rates[ii]) * num_events)
        hits = np.random.choice(times0, size=num_hits, replace=False)
        num_extra = int(approx_false_positive_rates[ii] * num_events)
        extra = np.random_choice(np.arange(num_timepoints), size=num_extra, replace=False).astype(float)
        times1 = np.sort(hits + extra)

        sorting_true.add_unit(ii+1, times0)
        sorting.add_unit(ii + 1, times1)
    
    for ii in range(len(extra_unit_firing_rates_hz)):
        num_events = int(duration_sec * extra_unit_firing_rates_hz[ii])
        times0 = np.random.choice(np.arange(num_timepoints), size=num_events, replace=False).astype(float)
        sorting.add_unit(len(true_firing_rates_hz)+ii+1, times0)

    # finish


    

if __name__ == '__main__':
    main()