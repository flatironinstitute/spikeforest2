from spikeforest2.experimental import sort

dir_in = '/mnt/ceph/users/jjun/groundtruth/hybrid_synth/static_tetrode/rec_4c_1200s_11/'
dir_out = dir_in + 'mountainsort4/firings.mda'
params = dict(detect_threshold=4, freq_min=300)
sort('mountainsort4', dir_in, dir_out, params=params)