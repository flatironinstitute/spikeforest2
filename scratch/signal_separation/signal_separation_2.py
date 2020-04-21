#!/usr/bin/env python

# Our goal here is to automatically separate signal from noise (or background signal) in an ephys recording

from spikeforest2_utils.autoextractors.mdaextractors.mdaextractors import MdaRecordingExtractor
from spikeforest2_utils import AutoRecordingExtractor, AutoSortingExtractor
import kachery as ka
import numpy as np
import hither

ka.set_config(fr='default_readonly')

# Load a recording
# recdir = 'sha1dir://fb52d510d2543634e247e0d2d1d4390be9ed9e20.synth_magland/datasets_noise10_K10_C4/001_synth'
recdir = 'sha1dir://fb52d510d2543634e247e0d2d1d4390be9ed9e20.synth_magland/datasets_noise20_K20_C4/001_synth'
# recdir = 'sha1dir://c0879a26f92e4c876cd608ca79192a84d4382868.manual_franklab/tetrode_600s/sorter1_1'
recobj = dict(
    raw=recdir + '/raw.mda',
    params=ka.load_object(recdir + '/params.json'),
    geom=np.genfromtxt(ka.load_file(recdir + '/geom.csv'), delimiter=',').tolist()
)

assert ka.load_file(recobj['raw']) is not None

def main():
    import spikeextractors as se
    from spikeforest2_utils import writemda32, AutoRecordingExtractor
    from sklearn.neighbors import NearestNeighbors
    from sklearn.cross_decomposition import PLSRegression
    import spikeforest_widgets as sw
    sw.init_electron()

    # bandpass filter
    with hither.config(container='default', cache='default_readwrite'):
        recobj2 = filter_recording.run(
            recobj=recobj,
            freq_min=300,
            freq_max=6000,
            freq_wid=1000
        ).retval
    
    detect_threshold = 3
    detect_interval = 200
    detect_interval_reference = 10
    detect_sign = -1
    num_events = 1000
    snippet_len = (200, 200)
    window_frac = 0.3
    num_passes = 20
    npca = 100
    max_t = 30000 * 100
    k = 20
    ncomp = 4
    
    R = AutoRecordingExtractor(recobj2)

    X = R.get_traces()
    
    sig = X.copy()
    if detect_sign < 0:
        sig = -sig
    elif detect_sign == 0:
        sig = np.abs(sig)
    sig = np.max(sig, axis=0)
    noise_level = np.median(np.abs(sig)) / 0.6745  # median absolute deviation (MAD)
    times_reference = detect_on_channel(sig, detect_threshold=noise_level*detect_threshold, detect_interval=detect_interval_reference, detect_sign=1, margin=1000)
    times_reference = times_reference[times_reference <= max_t]
    print(f'Num. reference events = {len(times_reference)}')

    snippets_reference = extract_snippets(X, reference_frames=times_reference, snippet_len=snippet_len)
    tt = np.linspace(-1, 1, snippets_reference.shape[2])
    window0 = np.exp(-tt**2/(2*window_frac**2))
    for j in range(snippets_reference.shape[0]):
        for m in range(snippets_reference.shape[1]):
            snippets_reference[j, m, :] = snippets_reference[j, m, :] * window0
    A_snippets_reference = snippets_reference.reshape(snippets_reference.shape[0], snippets_reference.shape[1] * snippets_reference.shape[2])

    print('PCA...')
    u, s, vh = np.linalg.svd(A_snippets_reference)
    components_reference = vh[0:npca, :].T
    features_reference = A_snippets_reference @ components_reference

    print('Setting up nearest neighbors...')
    nbrs = NearestNeighbors(n_neighbors=k + 1, algorithm='ball_tree').fit(features_reference)

    X_signal = np.zeros((R.get_num_channels(), R.get_num_frames()), dtype=np.float32)

    for passnum in range(num_passes):
        print(f'Pass {passnum}')
        sig = X.copy()
        if detect_sign < 0:
            sig = -sig
        elif detect_sign == 0:
            sig = np.abs(sig)
        sig = np.max(sig, axis=0)
        noise_level = np.median(np.abs(sig)) / 0.6745  # median absolute deviation (MAD)
        times = detect_on_channel(sig, detect_threshold=noise_level*detect_threshold, detect_interval=detect_interval, detect_sign=1, margin=1000)
        times = times[times <= max_t]
        print(f'Number of events: {len(times)}')
        if len(times) == 0:
            break
        snippets = extract_snippets(X, reference_frames=times, snippet_len=snippet_len)
        for j in range(snippets.shape[0]):
            for m in range(snippets.shape[1]):
                snippets[j, m, :] = snippets[j, m, :] * window0
        A_snippets = snippets.reshape(snippets.shape[0], snippets.shape[1] * snippets.shape[2])
        features = A_snippets @ components_reference
        
        print('Finding nearest neighbors...')
        distances, indices = nbrs.kneighbors(features)
        features2 = np.zeros(features.shape, dtype=features.dtype)
        print('PLS regression...')
        for j in range(features.shape[0]):
            print(f'{j+1} of {features.shape[0]}')
            inds0 = np.squeeze(indices[j, :])
            inds0 = inds0[1:] # TODO: it may not always be necessary to exclude the first -- how should we make that decision?
            f_neighbors = features_reference[inds0, :]
            pls = PLSRegression(n_components=ncomp)
            pls.fit(f_neighbors.T, features[j, :].T)
            features2[j, :] = pls.predict(f_neighbors.T).T
        A_snippets_denoised = features2 @ components_reference.T
        
        snippets_denoised = A_snippets_denoised.reshape(snippets.shape)

        for j in range(len(times)):
            t0 = times[j]
            snippet_denoised_0 = np.squeeze(snippets_denoised[j, :, :])
            X_signal[:, t0-snippet_len[0]:t0+snippet_len[1]] = X_signal[:, t0-snippet_len[0]:t0+snippet_len[1]] + snippet_denoised_0
            X[:, t0-snippet_len[0]:t0+snippet_len[1]] = X[:, t0-snippet_len[0]:t0+snippet_len[1]] - snippet_denoised_0

    S = np.concatenate((X_signal, X, R.get_traces()), axis=0)

    with hither.TemporaryDirectory() as tmpdir:
        raw_fname = tmpdir + '/raw.mda'
        writemda32(S, raw_fname)
        sig_recobj = recobj2.copy()
        sig_recobj['raw'] = ka.store_file(raw_fname)
    
    sw.TimeseriesView(recording=AutoRecordingExtractor(sig_recobj)).show()

    # np.save('snippets.npy', snippets)
    # np.save('snippets2.npy', snippets2)

def extract_snippets(X, *, reference_frames, snippet_len):
    if isinstance(snippet_len, (tuple, list, np.ndarray)):
        snippet_len_before = snippet_len[0]
        snippet_len_after = snippet_len[1]
    else:
        snippet_len_before = int((snippet_len + 1) / 2)
        snippet_len_after = snippet_len - snippet_len_before

    num_snippets = len(reference_frames)
    num_channels = X.shape[0]
    num_frames = X.shape[1]
    snippet_len_total = snippet_len_before + snippet_len_after
    # snippets = []
    snippets = np.zeros((num_snippets, num_channels, snippet_len_total))
    #TODO extract all waveforms in a chunk
    # pad_first = False
    # pad_last = False
    # pad_samples_first = 0
    # pad_samples_last = 0
    # snippet_idxs = np.array([], dtype=int)
    for i in range(num_snippets):
        snippet_chunk = np.zeros((num_channels, snippet_len_total))
        if (0 <= reference_frames[i]) and (reference_frames[i] < num_frames):
            snippet_range = np.array(
                [int(reference_frames[i]) - snippet_len_before, int(reference_frames[i]) + snippet_len_after])
            snippet_buffer = np.array([0, snippet_len_total])
            # The following handles the out-of-bounds cases
            if snippet_range[0] < 0:
                snippet_buffer[0] -= snippet_range[0]
                snippet_range[0] -= snippet_range[0]
            if snippet_range[1] >= num_frames:
                snippet_buffer[1] -= snippet_range[1] - num_frames
                snippet_range[1] -= snippet_range[1] - num_frames
            snippet_chunk[:, snippet_buffer[0]:snippet_buffer[1]] = X[:, snippet_range[0]:snippet_range[1]]
        snippets[i] = snippet_chunk
    return snippets

def knn_denoise(X, X_reference, *, k, ncomp):
    from sklearn.cross_decomposition import PLSRegression
    from sklearn.neighbors import NearestNeighbors
    # Xb = X * window

    print('PCA...')
    npca = np.minimum(300, X.shape[0])
    u, s, vh = np.linalg.svd(X)
    features = u[:, 0:npca] * s[0:npca]
    components = vh[0:npca, :]
    # s = s[0:npca]

    print('Nearest neighbors...')
    nbrs = NearestNeighbors(n_neighbors=k + 1, algorithm='ball_tree').fit(features)
    distances, indices = nbrs.kneighbors(features)
    
    features2 = np.zeros(features.shape, dtype=features.dtype)
    for j in range(X.shape[0]):
        print(f'{j+1} of {X.shape[0]}')
        inds0 = np.squeeze(indices[j, :])
        inds0 = inds0[1:]
        # Xbneighbors = Xb[inds0, :]
        f_neighbors = features[inds0, :]
        pls = PLSRegression(n_components=ncomp)
        # pls.fit(Xbneighbors.T, Xb[j, :].T)
        pls.fit(f_neighbors.T, features[j, :].T)
        features2[j, :] = pls.predict(f_neighbors.T).T
        # X2[j, :] = pls.predict(Xbneighbors.T).T
    print(features2.shape)
    print(components.shape)
    X2 = features2 @ components
    return X2

@hither.function(name='filter_recording', version='0.1.0')
@hither.container(default='docker://magland/spikeforest2:0.1.1')
@hither.local_module('../../spikeforest2_utils')
def filter_recording(recobj, freq_min=300, freq_max=6000, freq_wid=1000):
    from spikeforest2_utils import AutoRecordingExtractor
    from spikeforest2_utils import writemda32
    import spiketoolkit as st
    rx = AutoRecordingExtractor(recobj)
    rx2 = st.preprocessing.bandpass_filter(recording=rx, freq_min=freq_min, freq_max=freq_max, freq_wid=freq_wid)
    recobj2 = recobj.copy()
    with hither.TemporaryDirectory() as tmpdir:
        raw_fname = tmpdir + '/raw.mda'
        if not writemda32(rx2.get_traces(), raw_fname):
            raise Exception('Unable to write output file.')
        recobj2['raw'] = ka.store_file(raw_fname)
        return recobj2

def detect_on_channel(data,*,detect_threshold,detect_interval,detect_sign,margin=0):
    # Adjust the data to accommodate the detect_sign
    # After this adjustment, we only need to look for positive peaks
    if detect_sign<0:
        data=data*(-1)
    elif detect_sign==0:
        data=np.abs(data)
    elif detect_sign>0:
        pass

    data=data.ravel()
        
    #An event at timepoint t is flagged if the following two criteria are met:
    # 1. The value at t is greater than the detection threshold (detect_threshold)
    # 2. The value at t is greater than the value at any other timepoint within plus or minus <detect_interval> samples
    
    # First split the data into segments of size detect_interval (don't worry about timepoints left over, we assume we have padding)
    N=len(data)
    S2=int(np.floor(N/detect_interval))
    N2=S2*detect_interval
    data2=np.reshape(data[0:N2],(S2,detect_interval))
    
    # Find the maximum on each segment (these are the initial candidates)
    max_inds2=np.argmax(data2,axis=1)
    max_inds=max_inds2+detect_interval*np.arange(0,S2)
    max_vals=data[max_inds]
    
    # The following two tests compare the values of the candidates with the values of the neighbor candidates
    # If they are too close together, then discard the one that is smaller by setting its value to -1
    # Actually, this doesn't strictly satisfy the above criteria but it is close
    # TODO: fix the subtlety
    max_vals[ np.where((max_inds[0:-1]>=max_inds[1:]-detect_interval) & (max_vals[0:-1]<max_vals[1:]))[0] ]=-1
    max_vals[1+np.array( np.where((max_inds[1:]<=max_inds[0:-1]+detect_interval) & (max_vals[1:]<=max_vals[0:-1]))[0] )]=-1
    
    # Finally we use only the candidates that satisfy the detect_threshold condition
    times=max_inds[ np.where(max_vals>=detect_threshold)[0] ]
    if margin>0:
        times=times[np.where((times>=margin)&(times<N-margin))[0]]

    return times


if __name__ == '__main__':
    main()

