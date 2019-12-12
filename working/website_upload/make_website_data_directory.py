#!/usr/bin/env python

import argparse
import os
import json

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
    parser.add_argument('--output_dir', '-o', help='The output directory for saving the files.')

    args = parser.parse_args()

    output_dir = args.output_dir

    if os.path.exists(output_dir):
        raise Exception('Output directory already exists: {}'.format(output_dir))

    os.mkdir(output_dir)

    print('Loading spike-front results object...')
    with open(args.path, 'r') as f:
        obj = json.load(f)

    StudySets = obj['StudySets']
    SortingResults = obj['SortingResults']
    Sorters = obj['Sorters']
    Algorithms = obj['Algorithms']
    StudyAnalysisResults = obj['StudyAnalysisResults']
    General = obj['General']

    print('Saving {} study sets to {}/StudySets.json'.format(len(StudySets), output_dir))
    with open(output_dir + '/StudySets.json', 'w') as f:
        json.dump(StudySets, f)

    print('Saving {} sorting results to {}/SortingResults.json'.format(len(SortingResults), output_dir))
    with open(output_dir + '/SortingResults.json', 'w') as f:
        json.dump(SortingResults, f)

    print('Saving {} sorters to {}/Sorters.json'.format(len(Sorters), output_dir))
    with open(output_dir + '/Sorters.json', 'w') as f:
        json.dump(Sorters, f)

    print('Saving {} algorithms to {}/Algorithms.json'.format(len(Algorithms), output_dir))
    with open(output_dir + '/Algorithms.json', 'w') as f:
        json.dump(Algorithms, f)

    print('Saving {} study analysis results to {}/StudyAnalysisResults.json'.format(len(StudySets), output_dir))
    with open(output_dir + '/StudyAnalysisResults.json', 'w') as f:
        json.dump(StudyAnalysisResults, f)

    print('Saving general info to {}/General.json'.format(output_dir))
    with open(output_dir + '/General.json', 'w') as f:
        json.dump(General, f)

if __name__ == "__main__":
    main()
