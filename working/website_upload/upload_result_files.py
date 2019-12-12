#!/usr/bin/env python

import argparse
import os
import json
import kachery as ka
from mountaintools import client as mt

help_txt = """
This script saves collections in the following .json files in an output directory

Algorithms.json
Sorters.json
SortingResults.json
StudySets.json
StudyAnalysisResults.json
"""


def main():
    parser = argparse.ArgumentParser(description=help_txt, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('path', help='Path to the assembled website data in .json format')

    args = parser.parse_args()

    print('Loading spike-front results object...')
    with open(args.path, 'r') as f:
        obj = json.load(f)

    SortingResults = obj['SortingResults']

    for sr in SortingResults:
        print(sr['studyName'], sr['recordingName'])
        console_out_fname = ka.load_file(sr['consoleOut'])
        mt.createSnapshot(path=console_out_fname, upload_to='spikeforest.public')
        if sr.get('firings', None) is not None:
            firings_fname = ka.load_file(sr['firings'])
            mt.createSnapshot(path=firings_fname, upload_to='spikeforest.public')

if __name__ == "__main__":
    main()
