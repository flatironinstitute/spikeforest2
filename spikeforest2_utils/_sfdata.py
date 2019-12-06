# from PIL import Image
import pandas as pd
from typing import Union, List
import kachery as ka


class SFStudy():
    def __init__(self, obj: dict):
        self._obj = obj
        self._recordings_by_name: dict = dict()
        self._recording_names: List[str] = []

    def getObject(self):
        return self._obj

    def name(self):
        return self._obj.get('recording_name', self._obj.get('name'))

    def description(self):
        return self._obj['description']

    def addRecording(self, obj: dict):
        name = obj.get('recording_name', obj.get('name'))
        if name in self._recordings_by_name:
            print('Recording already in study: ' + name)
        else:
            self._recording_names.append(name)
            D = SFRecording(obj, self)
            self._recordings_by_name[name] = D

    def recordingNames(self):
        return self._recording_names

    def recording(self, name: str):
        return self._recordings_by_name.get(name, None)



class SFRecording():
    def __init__(self, obj: dict, study: SFStudy):
        self._obj = obj
        self._sorting_result_names : List[str] = []
        self._sorting_results_by_name: dict = dict()
        self._summary_result: Union[dict, None] = None
        if 'summary' in obj:
            self._summary_result = obj['summary']
        self._study = study

    def getObject(self):
        return self._obj

    def getSummaryObject(self):
        return self._summary_result

    def study(self):
        return self._study

    def name(self):
        return self._obj.get('recording_name', self._obj.get('name'))

    def description(self):
        return self._obj['description']

    def directory(self):
        return self._obj['directory']

    # def recordingFileIsLocal(self):
    #     fname = self.directory() + '/raw.mda'
    #     fname2 = mt.findFile(fname, local_only=True)
    #     if fname2 and (not _is_url(fname2)):
    #         return True
    #     return False

    # def realizeRecordingFile(self):
    #     fname = self.directory() + '/raw.mda'
    #     return mt.realizeFile(fname)

    # def firingsTrueFileIsLocal(self):
    #     fname = self.directory() + '/firings_true.mda'
    #     fname2 = mt.findFile(fname, local_only=True)
    #     if fname2 and (not _is_url(fname2)):
    #         return True
    #     return False

    # def realizeFiringsTrueFile(self):
    #     fname = self.directory() + '/firings_true.mda'
    #     return mt.realizeFile(fname)

    # def recordingExtractor(self, download: bool=False):
    #     X = SFMdaRecordingExtractor(dataset_directory=self.directory(), download=download)
    #     if 'channels' in self._obj:
    #         if self._obj['channels']:
    #             X = si.SubRecordingExtractor(parent_recording=X, channel_ids=self._obj['channels'])
    #     return X

    def sortingTrue(self):
        return SFMdaSortingExtractor(firings_file=self.directory() + '/firings_true.mda')

    def plotNames(self):
        if not self._summary_result:
            return []
        plots = self._summary_result.get('plots', dict())
        return list(plots.keys())

    # def plot(self, name: str, format: str='image'):
    #     assert self._summary_result is not None, 'No summary result found'
    #     plots = self._summary_result.get('plots', dict())
    #     url = plots[name]
    #     if format == 'url':
    #         return url
    #     else:
    #         path = mt.realizeFile(url)
    #         if format == 'image':
    #             return Image.open(path)
    #         elif format == 'path':
    #             return path
    #         else:
    #             raise Exception('Invalid format: ' + format)

    def trueUnitsInfo(self, format: str='dataframe'):
        if not self._summary_result:
            return None
        B = ka.load_object(self._summary_result['true_units_info'])
        if format == 'json':
            return B
        elif format == 'dataframe':
            return pd.DataFrame(B)
        else:
            raise Exception('Invalid format: ' + format)

    def setSummaryResult(self, obj: dict):
        self._summary_result = obj

    def addSortingResult(self, obj: dict):
        sorter_name = obj['sorter']['name']
        if sorter_name in self._sorting_results_by_name:
            print('Sorting result already in recording: {}'.format(sorter_name))
        else:
            R = SFSortingResult(obj, self)
            self._sorting_result_names.append(sorter_name)
            self._sorting_results_by_name[sorter_name] = R

    def sortingResultNames(self):
        return self._sorting_result_names

    def sortingResult(self, name: str):
        return self._sorting_results_by_name.get(name, None)



class SFSortingResult():
    def __init__(self, obj: dict, recording: SFRecording):
        self._obj = obj
        self._recording = recording

    def getObject(self):
        return self._obj

    def recording(self):
        return self._recording

    def sorterName(self):
        return self._obj['sorter']['name']

    def plotNames(self):
        plots = self._obj['summary'].get('plots', dict())
        return list(plots.keys())

    def sorting(self):
        return SFMdaSortingExtractor(firings_file=self._obj['firings'])

    # def plot(self, name: str, format: str='image'):
    #     plots = self._obj['summary'].get('plots', dict())
    #     url = plots[name]
    #     if format == 'url':
    #         return url
    #     else:
    #         path = mt.realizeFile(url)
    #         if format == 'image':
    #             return Image.open(path)
    #         elif format == 'path':
    #             return path
    #         else:
    #             raise Exception('Invalid format: ' + format)

    def comparisonWithTruth(self, *, format: str='dataframe'):
        A = self._obj['comparison_with_truth']
        if not A:
            return None
        B = ka.load_object(A['json'])
        if format == 'json':
            return B
        elif format == 'dataframe':
            return pd.DataFrame(B).transpose()
        else:
            raise Exception('Invalid format: ' + format)
    
    def sortedUnitsInfo(self):
        A = self._obj.get('sorted_units_info', None)
        if not A:
            return None
        return ka.load_object(A)



class SFData():
    def __init__(self):
        self._studies_by_name = dict()
        self._study_names = []

    def loadStudy(self, study: dict):
        name = study['name']
        if name in self._studies_by_name:
            print('Study already loaded: ' + name)
        else:
            self._study_names.append(study['name'])
            S = SFStudy(study)
            self._studies_by_name[name] = S

    def loadStudies(self, studies: List[dict]):
        for study in studies:
            self.loadStudy(study)

    def loadRecording(self, recording: dict):
        study = recording.get('study_name', recording.get('study_name', recording.get('study')))
        self._studies_by_name[study].addRecording(recording)

    def loadRecordings2(self, recordings: List[dict]):
        for recording in recordings:
            self.loadRecording(recording)

    def loadSortingResults(self, sorting_results: List[dict]):
        for result in sorting_results:
            self.loadSortingResult(result)

    def loadSortingResult(self, X: dict):
        study_name = X['recording'].get('study_name', X['recording'].get('study'))
        recording_name = X['recording'].get('recording_name', X['recording'].get('name'))
        # sorter_name=X['sorter']['name']
        S = self.study(study_name)
        if S:
            D = S.recording(recording_name)
            if D:
                D.addSortingResult(X)
            else:
                print('Warning: recording not found: ' + recording_name)
        else:
            print('Warning: study not found: ' + study_name)

    def studyNames(self):
        return self._study_names

    def study(self, name: str) -> Union[SFStudy, None]:
        return self._studies_by_name.get(name, None)


def _is_url(path):
    return (path.startswith('http://') or path.startswith('https://'))
