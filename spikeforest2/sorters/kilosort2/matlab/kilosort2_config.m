function ops = kilosort2_config(params)
% params: nchan, sample_rate, dat_file, freq_min, projection_threshold, minFR, sigmaMask, preclust_threshold, kilo_thresh, use_car, nPCs, chanmap_file

ops.NchanTOT            = params.nchan;           % total number of channels (omit if already in chanMap file)
ops.Nchan               = params.nchan;           % number of active channels (omit if already in chanMap file)
ops.fs                  = params.sample_rate;     % sampling rate

ops.datatype            = 'dat';  % binary ('dat', 'bin') or 'openEphys'
ops.fbinary             = params.dat_file; % will be created for 'openEphys'
ops.fproc               = 'temp_wh.dat'; % residual from RAM of preprocessed data
% ops.root                = fpath; % 'openEphys' only: where raw files are
% define the channel map as a filename (string) or simply an array
ops.chanMap             = params.chanmap_file; % make this file using createChannelMapFile.m

% frequency for high pass filtering (150)
ops.fshigh = params.freq_min;

% minimum firing rate on a "good" channel (0 to skip)
ops.minfr_goodchannels = 0.1; 

% threshold on projections (like in Kilosort1, can be different for last pass like [10 4])
ops.Th = params.projection_threshold;

% how important is the amplitude penalty (like in Kilosort1, 0 means not used, 10 is average, 50 is a lot) 
ops.lam = 10;  

% splitting a cluster at the end requires at least this much isolation for each sub-cluster (max = 1)
ops.AUCsplit = 0.9; 

% minimum spike rate (Hz), if a cluster falls below this for too long it gets removed
ops.minFR = params.minFR;

% number of samples to average over (annealed from first to second value) 
ops.momentum = [20 400]; 

% spatial constant in um for computing residual variance of spike
ops.sigmaMask = params.sigmaMask; 

% threshold crossings for pre-clustering (in PCA projection space)
ops.ThPre = params.preclust_threshold;
%% danger, changing these settings can lead to fatal errors
% options for determining PCs
ops.spkTh           = -params.kilo_thresh;      % spike threshold in standard deviations (-6)
ops.reorder         = 1;       % whether to reorder batches for drift correction. 
ops.nskip           = 25;  % how many batches to skip for determining spike PCs

ops.CAR             = params.use_car; % perform CAR

ops.GPU                 = 1; % has to be 1, no CPU version yet, sorry
% ops.Nfilt             = 1024; % max number of clusters
ops.nfilt_factor        = 4; % max number of clusters per good channel (even temporary ones)
ops.ntbuff              = 64;    % samples of symmetrical buffer for whitening and spike detection
ops.NT                  = 64*1024+ ops.ntbuff; % must be multiple of 32 + ntbuff. This is the batch size (try decreasing if out of memory). 
ops.whiteningRange      = 32; % number of channels to use for whitening each channel
ops.nSkipCov            = 25; % compute whitening matrix from every N-th batch
ops.scaleproc           = 200;   % int16 scaling of whitened data
ops.nPCs                = params.nPCs; % how many PCs to project the spikes into
ops.useRAM              = 0; % not yet available

%%