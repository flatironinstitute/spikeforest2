from ._sfdata import SFData

def aggregate_sorting_results(studies, recordings, sorting_results):
    SF = SFData()
    SF.loadStudies(studies=studies)
    SF.loadRecordings2(recordings=recordings)
    SF.loadSortingResults(sorting_results=sorting_results)

    aggregated_sorting_results = dict(
        recording_sorting_results=[],
        study_sorting_results=[]
    )
    for study_name in SF.studyNames():
        print('study: ' + study_name)
        S = SF.study(study_name)
        if len(S.recordingNames()) > 0:
            first_recording = S.recording(S.recordingNames()[0])
            sorter_names = first_recording.sortingResultNames()

            for srname in sorter_names:
                print('sorter: ' + srname)

                study_results0 = dict(
                    recording_indices=[],
                    true_unit_ids=[],
                    true_unit_snrs=[],
                    true_unit_firing_rates=[],
                    num_matches=[],
                    num_false_positives=[],
                    num_false_negatives=[]
                )

                comparisons_all_exist = True
                some_comparison_exists = False
                for recording_index, rname in enumerate(S.recordingNames()):
                    rec = S.recording(rname)
                    SR = rec.sortingResult(srname)
                    comparison = SR.comparisonWithTruth(format='json')
                    if comparison is None:
                        comparisons_all_exist = False
                    else:
                        some_comparison_exists = True
                if not comparisons_all_exist:
                    print('WARNING: Comparisons do not all exist for sorter sorter: {}'.format(srname))
                if some_comparison_exists:
                    for recording_index, rname in enumerate(S.recordingNames()):
                        rec = S.recording(rname)
                        true_units_info = rec.trueUnitsInfo(format='json')
                        true_units_info_by_id = dict()
                        for true_unit in true_units_info:
                            true_units_info_by_id[true_unit['unit_id']] = true_unit
                        SR = rec.sortingResult(srname)
                        comparison = SR.comparisonWithTruth(format='json')
                        if comparison is None:
                            # put in a zero comparison
                            comparison = dict()
                            for true_unit in true_units_info:
                                comparison[true_unit['unit_id']] = dict(
                                    unit_id=true_unit['unit_id'],
                                    num_false_positives=0,
                                    num_false_negatives=true_unit['num_events'],
                                    num_matches=0
                                )
                        if comparison is not None:
                            recording_results0 = dict(
                                true_unit_ids=[],
                                true_unit_snrs=[],
                                true_unit_firing_rates=[],
                                num_matches=[],
                                num_false_positives=[],
                                num_false_negatives=[]
                            )

                            ok: bool = True
                            error: str = ''
                            for key0 in comparison.keys():
                                unit = comparison[key0]
                                # best_unit = unit['best_unit']
                                unit_id = unit['unit_id']
                                true_unit = true_units_info_by_id[unit_id]

                                recording_results0['true_unit_ids'].append(unit_id)
                                recording_results0['true_unit_snrs'].append(round(true_unit['snr'], 3))
                                recording_results0['true_unit_firing_rates'].append(
                                    round(true_unit['firing_rate'], 3))
                                if 'num_false_positives' in unit:
                                    recording_results0['num_matches'].append(unit['num_matches'])
                                    recording_results0['num_false_positives'].append(unit['num_false_positives'])
                                    recording_results0['num_false_negatives'].append(unit['num_false_negatives'])
                                else:
                                    ok = False
                                    error = 'missing field: num_false_positives'
                                    break
                            if ok:
                                recording_sorting_result = dict(
                                    study=study_name,
                                    recording=rname,
                                    sorter=srname,
                                    true_unit_ids=recording_results0['true_unit_ids'],
                                    true_unit_snrs=recording_results0['true_unit_snrs'],
                                    true_unit_firing_rates=recording_results0['true_unit_firing_rates'],
                                    num_matches=recording_results0['num_matches'],
                                    num_false_positives=recording_results0['num_false_positives'],
                                    num_false_negatives=recording_results0['num_false_negatives']
                                )
                                aggregated_sorting_results['recording_sorting_results'].append(recording_sorting_result)
                            else:
                                print('Warning: ' + error)

                            study_results0['recording_indices'].extend([recording_index] * len(recording_results0['true_unit_ids']))
                            study_results0['true_unit_ids'].extend(recording_results0['true_unit_ids'])
                            study_results0['true_unit_snrs'].extend(recording_results0['true_unit_snrs'])
                            study_results0['true_unit_firing_rates'].extend(recording_results0['true_unit_firing_rates'])
                            study_results0['num_matches'].extend(recording_results0['num_matches'])
                            study_results0['num_false_positives'].extend(recording_results0['num_false_positives'])
                            study_results0['num_false_negatives'].extend(recording_results0['num_false_negatives'])

                    study_sorting_result = dict(
                        study=study_name,
                        sorter=srname,
                        true_unit_recording_indices=study_results0['recording_indices'],
                        true_unit_ids=study_results0['true_unit_ids'],
                        true_unit_snrs=study_results0['true_unit_snrs'],
                        true_unit_firing_rates=study_results0['true_unit_firing_rates'],
                        num_matches=study_results0['num_matches'],
                        num_false_positives=study_results0['num_false_positives'],
                        num_false_negatives=study_results0['num_false_negatives']
                    )
                    aggregated_sorting_results['study_sorting_results'].append(study_sorting_result)
                else:
                    print('WARNING: Skipping aggregation for sorter because no comparisons exist: {}'.format(srname))

    return aggregated_sorting_results
