#!/usr/bin/env python

import argparse
import json
from mountaintools import client as mt


def main():

    parser = argparse.ArgumentParser(description='update spike-front analysis history')
    parser.add_argument(
        '--delete-and-init',
        help='Use this only the first time. Will wipe out the history.',
        action='store_true'
    )
    parser.add_argument(
        '--show',
        help='Show the analysis history.',
        action='store_true'
    )

    args = parser.parse_args()

    history_path = 'key://pairio/spikeforest/spike-front-analysis-history.json'
    results_path = 'output.json'

    mt.configDownloadFrom(['spikeforest.kbucket', 'spikeforest.public'])
    if args.delete_and_init:
        print('Initializing analysis history...')
        mt.createSnapshot(
            mt.saveObject(object=dict(analyses=[])),
            dest_path=history_path,
            upload_to='spikeforest.public'
        )
        print('Done.')
        return

    print('Loading history...')
    history = mt.loadObject(path=history_path)
    assert history, 'Unable to load history'

    if args.show:
        for aa in history['analyses']:
            print('===============================================================')
            print('ANALYSIS: {}'.format(aa['General']['dateUpdated']))
            print('PATH: {}'.format(aa['path']))
            print(json.dumps(aa['General'], indent=4))
            print('')
        return

    print('Loading current results...')
    spike_front_results = mt.loadObject(path=results_path)
    assert spike_front_results, 'Unable to load current results'

    sha1_url = mt.saveObject(object=spike_front_results, basename='analysis.json')
    for aa in history['analyses']:
        if aa['path'] == sha1_url:
            print('Analysis already stored in history.')
            return

    history['analyses'].append(
        dict(
            path=sha1_url,
            General=spike_front_results['General'][0]
        )
    )

    print('Saving updated history to {}'.format(history_path))
    mt.createSnapshot(
        mt.saveObject(object=history),
        dest_path=history_path,
        upload_to='spikeforest.public'
    )
    print('Done.')

if __name__ == "__main__":
    main()
