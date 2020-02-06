


import argparse
import spikeforest_widgets as sw
from spikeforest2_utils import AutoRecordingExtractor
import kachery as ka

sw.init_electron()

ka.set_config(fr='default_readonly')

parser = argparse.ArgumentParser(description='Browse a SpikeForest analysis')
parser.add_argument('--path', help='Path to the directory to browse', required=True)

args = parser.parse_args()

X = sw.DirectoryView(
    path = args.path
)
X.show()