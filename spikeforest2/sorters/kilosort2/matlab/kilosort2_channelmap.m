function kilosort2_channelmap(fname, params)
% params: nchan, xcoords, ycoords, kcoords, sample_rate

%  create a channel map file

Nchannels = params.nchan; % number of channels
connected = true(Nchannels, 1);
chanMap   = 1:Nchannels;
chanMap0ind = chanMap - 1;

xcoords = params.xcoords;
ycoords = params.ycoords;
kcoords   = params.kcoords;

fs = params.sample_rate; % sampling frequency
save(fname, ...
    'chanMap','connected', 'xcoords', 'ycoords', 'kcoords', 'chanMap0ind', 'fs')
