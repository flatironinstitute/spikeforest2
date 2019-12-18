import json
import hither
from spikeforest2_utils import AutoSortingExtractor
from spikeforest2_utils import AutoRecordingExtractor

@hither.function('compare_with_truth', '0.1.0')
@hither.input_file('sorting_path')
@hither.input_file('sorting_true_path')
@hither.output_file('json_out')
@hither.container(default='docker://magland/spikeforest2:0.1.0')
@hither.local_module('../../spikeforest2_utils')
def compare_with_truth(sorting_path, sorting_true_path, json_out):
    from spikeforest2_utils import SortingComparison
    sorting = AutoSortingExtractor(sorting_path)
    sorting_true = AutoSortingExtractor(sorting_true_path)
    SC = SortingComparison(sorting_true, sorting, delta_tp=30)
    df = _get_comparison_data_frame(comparison=SC)
    obj = df.transpose().to_dict()
    with open(json_out, 'w') as f:
        json.dump(obj, f, indent=4)

def _get_comparison_data_frame(*, comparison):
    import pandas as pd
    SC = comparison

    unit_properties = []  # snr, etc? these would need to be properties in the sortings of the comparison

    # Compute events counts
    sorting1 = SC.getSorting1()
    sorting2 = SC.getSorting2()
    unit1_ids = sorting1.get_unit_ids()
    unit2_ids = sorting2.get_unit_ids()
    # N1 = len(unit1_ids)
    # N2 = len(unit2_ids)
    event_counts1 = dict()
    for _, u1 in enumerate(unit1_ids):
        times1 = sorting1.get_unit_spike_train(unit_id=u1)
        event_counts1[u1] = len(times1)
    event_counts2 = dict()
    for _, u2 in enumerate(unit2_ids):
        times2 = sorting2.get_unit_spike_train(unit_id=u2)
        event_counts2[u2] = len(times2)

    rows = []
    for _, unit1 in enumerate(unit1_ids):
        unit2 = SC.getBestUnitMatch1(unit1)
        if unit2 >= 0:
            num_matches = SC.getMatchingEventCount(unit1, unit2)
            num_false_negatives = event_counts1[unit1] - num_matches
            num_false_positives = event_counts2[unit2] - num_matches
        else:
            num_matches = 0
            num_false_negatives = event_counts1[unit1]
            num_false_positives = 0
        row0 = {
            'unit_id': unit1,
            'accuracy': _safe_frac(num_matches, num_false_positives + num_false_negatives + num_matches),
            'best_unit': unit2,
            'matched_unit': SC.getMappedSorting1().getMappedUnitIds(unit1),
            'num_matches': num_matches,
            'num_false_negatives': num_false_negatives,
            'num_false_positives': num_false_positives,
            'f_n': _safe_frac(num_false_negatives, num_false_negatives + num_matches),
            'f_p': _safe_frac(num_false_positives, num_false_positives + num_matches)
        }
        for prop in unit_properties:
            pname = prop['name']
            row0[pname] = SC.getSorting1().get_unit_property(unit_id=int(unit1), property_name=pname)
        rows.append(row0)

    df = pd.DataFrame(rows)
    fields = ['unit_id']
    fields = fields + ['accuracy', 'best_unit', 'matched_unit', 'num_matches', 'num_false_negatives', 'num_false_positives', 'f_n', 'f_p']
    for prop in unit_properties:
        pname = prop['name']
        fields.append(pname)
    df = df[fields]
    df['accuracy'] = df['accuracy'].map('{:,.4f}'.format)
    # df['Best match'] = df['Accuracy'].map('{:,.2f}'.format)
    df['f_n'] = df['f_n'].map('{:,.4f}'.format)
    df['f_p'] = df['f_p'].map('{:,.4f}'.format)
    return df


def _safe_frac(numer, denom):
    if denom == 0:
        return 0
    return float(numer) / denom
