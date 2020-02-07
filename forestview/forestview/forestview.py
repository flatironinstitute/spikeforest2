


import argparse
import spikeforest_widgets as sw
from spikeforest2_utils import AutoRecordingExtractor
import kachery as ka

sw.init_electron()

ka.set_config(fr='default_readonly')

parser = argparse.ArgumentParser(description='Browse a SpikeForest analysis')
# parser.add_argument('--path', help='Path to the analysis JSON file', required=True)

args = parser.parse_args()

R = AutoRecordingExtractor('sha1dir://49b1fe491cbb4e0f90bde9cfc31b64f985870528.paired_boyden32c/531_2_1')

X = sw.TimeseriesView(
    recording = R
)
X.show()