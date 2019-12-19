#!/usr/bin/env python

import argparse
import os
import json
import kachery as ka
from mountaintools import client as mt

help_txt = """
Upload result files to kachery
"""


def main():
    parser = argparse.ArgumentParser(description=help_txt, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('path', help='Path to the assembled website data in .json format')
    parser.add_argument('--console-out', help='Store console output', action='store_true')
    parser.add_argument('--firings', help='Store firings output', action='store_true')

    args = parser.parse_args()

    print('Loading spike-front results object...')
    with open(args.path, 'r') as f:
        obj = json.load(f)

    SortingResults = obj['SortingResults']

    for sr in SortingResults:
        print(sr['studyName'], sr['recordingName'])
        console_out_fname = ka.load_file(sr['consoleOut'])
        if args.console_out:
            mt.createSnapshot(path=console_out_fname, upload_to='spikeforest.public')
            ka.store_file(console_out_fname, to='default_readwrite')
        if args.firings:
            if sr.get('firings', None) is not None:
                firings_fname = ka.load_file(sr['firings'])
                mt.createSnapshot(path=firings_fname, upload_to='spikeforest.public')
                ka.store_file(firings_fname, to='default_readwrite')

if __name__ == "__main__":
    main()
