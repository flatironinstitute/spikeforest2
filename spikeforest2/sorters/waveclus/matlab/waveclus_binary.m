function waveclus_binary(vcDir_temp, vcFile_raw, vcFile_mda, sRateHz)
% Arguments
% -----
% sRateHz: sampling rate
% vcFile_raw: input raw .mda file (raw.mda)
% vcFile_mda: output .mda file (firings.mda)

try
    if isstr(sRateHz)
        % need to do this because on command-line, sRateHz comes in as a string
        sRateHz = str2double(sRateHz)
    end;
    % convert input to matlab format. flip polarity for positive detection
    vcFile_mat = fullfile(vcDir_temp, 'raw.mat');
    data = double(readmda(vcFile_raw) * -1);
    sr = sRateHz;
    fprintf('Converting file %s -> %s\n', vcFile_raw, vcFile_mat)
    try
        save(vcFile_mat, 'data', 'sr', '-v7.3', '-nocompression'); %faster    
    catch
        save(vcFile_mat, 'data', 'sr');
    end
    
    % Run waveclus batch mode. supply parameter file (set sampling rate)
    S_par = set_parameters_spf();
    S_par.sr = sRateHz;
    cd(vcDir_temp);
    Get_spikes(vcFile_mat, 'par', S_par);
    vcFile_spikes = strrep(vcFile_mat, '.mat', '_spikes.mat');
    Do_clustering(vcFile_spikes, 'make_plots', false);
    [vcDir_, vcFile_, vcExt_] = fileparts(vcFile_mat);
    vcFile_cluster = fullfile(vcDir_, ['times_', vcFile_, vcExt_]);
    
    % parse output and save
    S0 = load(vcFile_cluster);
    mr_waveclus = S0.cluster_class;
    viSpk_keep = find(mr_waveclus(:,1)>0);
    nSpikes = numel(viSpk_keep);
    mr_mda = ones(nSpikes, 3, 'double');
    mr_mda(:,2) = mr_waveclus(viSpk_keep,2)/1000 * sRateHz; % time
    mr_mda(:,3) = mr_waveclus(viSpk_keep,1); % cluster
    
    writemda(mr_mda', vcFile_mda, 'float64');
    fprintf('p_waveclus: wrote to %s\n', vcFile_mda);    
catch ME
    arrayfun(@(x)disp(x), ME.stack);
    fprintf('----------------------------------------\n');
    disp(ME)
    fprintf('----------------------------------------\n');

    quit(1);
end
quit(0);
    
end %func
    

%--------------------------------------------------------------------------
function edit_prm_file_(vcFile_from, vcFile_to, P)
% 1. read lines from vcFile_from
% 2. parse lines from vcFile_from
% 3. replace fields from S_opt
% 3. output to vcFile_to

csLines = file2cellstr_(vcFile_from); %read to cell string
csLines_var = first_string_(csLines);

csName = fieldnames(P);
csValue = cellfun(@(vcField)P.(vcField), csName, 'UniformOutput',0);
for i=1:numel(csName)
    vcName = csName{i}; %find field name with 
    if isstruct(csValue{i}), continue; end %do not write struct
    vcValue = field2str_(csValue{i});
    iLine = find(strcmpi(csLines_var, vcName));
    if numel(iLine)>1 % more than one variable found
        error(['edit_prm_file_: Multiple copies of variables found: ' vcName]); 
    elseif isempty(iLine) %did not find, append
        csLines{end+1} = sprintf('%s = %s;', vcName, vcValue);
    else    
        vcComment = getCommentExpr_(csLines{iLine});        
        csLines{iLine} = sprintf('%s = %s;\t\t\t%s', vcName, vcValue, vcComment);    
    end
end
cellstr2file_(vcFile_to, csLines);
end %func


%--------------------------------------------------------------------------
% 8/2/17 JJJ: Test and documentation. Added strtrim
function cs = first_string_(cs)
    % Return the first string, which is typically a variable name
    
if ischar(cs), cs = {cs}; end

for i=1:numel(cs)
    cs{i} = strtrim(cs{i});
    if isempty(cs{i}), continue; end
    cs1 = textscan(cs{i}, '%s', 'Delimiter', {' ','='});
    cs1 = cs1{1};
    cs{i} = cs1{1};
end
end %func


%--------------------------------------------------------------------------
% 8/2/17 JJJ: Documentation and test
function csLines = file2cellstr_(vcFile)
% read text file to a cell string
try
    fid = fopen(vcFile, 'r');
    csLines = {};
    while ~feof(fid), csLines{end+1} = fgetl(fid); end
    fclose(fid);
    csLines = csLines';
catch
    csLines = {};
end
end %func


%--------------------------------------------------------------------------
% 8/2/17 JJJ: Test and documentation
function cellstr2file_(vcFile, csLines, fVerbose)
% Write a cellstring to a text file
if nargin<3, fVerbose = 0; end
vcDir = fileparts(vcFile);
mkdir_(vcDir);
fid = fopen(vcFile, 'w');
for i=1:numel(csLines)
    fprintf(fid, '%s\n', csLines{i});
end
fclose(fid);
if fVerbose
    fprintf('Wrote to %s\n', vcFile);
end
end %func


%--------------------------------------------------------------------------
% 8/2/17 JJJ: Documentation and test
function vcComment = getCommentExpr_(vcExpr)
% Return the comment part of the Matlab code

iStart = strfind(vcExpr, '%');
if isempty(iStart), vcComment = ''; return; end
vcComment = vcExpr(iStart(1):end);
end %func
    


%--------------------------------------------------------------------------
function fCreatedDir = mkdir_(vcDir)
% make only if it doesn't exist. provide full path for dir
fCreatedDir = exist_dir_(vcDir);
if ~fCreatedDir
    try
        mkdir(vcDir); 
    catch
        fCreatedDir = 0;
    end
end
end %func


%---------------------------------------------------------------------------
% 8/2/17 JJJ: Test and documentation
function vcStr = field2str_(val, fDoubleQuote)
% convert a value to a strong
if nargin<2, fDoubleQuote = false; end

switch class(val)
    case {'int', 'int16', 'int32', 'uint16', 'uint32'}
        vcFormat = '%d';
    case {'double', 'single'}
        vcFormat = '%g';
        if numel(val)==1
            if mod(val(1),1)==0, vcFormat = '%d'; end
        end
    case 'char'
        if fDoubleQuote
            vcStr = sprintf('"%s"', val);
        else
            vcStr = sprintf('''%s''', val);
        end
        return;
    case 'cell'
        vcStr = '{';
        for i=1:numel(val)
            vcStr = [vcStr, field2str_(val{i})];
            if i<numel(val), vcStr = [vcStr, ', ']; end
        end
        vcStr = [vcStr, '}'];
        return;
    case 'logical'
        vcFormat = '%s';
        if val
            vcStr = '1';
        else
            vcStr = '0';
        end
    otherwise
        vcStr = '';
        fprintf(2, 'field2str_: unsupported format: %s\n', class(val));
        return;
end

if numel(val) == 1
    vcStr = sprintf(vcFormat, val);
else % Handle a matrix or array
    vcStr = '[';
    for iRow=1:size(val,1)
        for iCol=1:size(val,2)
            vcStr = [vcStr, field2str_(val(iRow, iCol))];
            if iCol < size(val,2), vcStr = [vcStr, ', ']; end
        end
        if iRow<size(val,1), vcStr = [vcStr, '; ']; end
    end
    vcStr = [vcStr, ']'];
end
end %func


%--------------------------------------------------------------------------
% 8/7/2018 JJJ
function flag = exist_dir_(vcDir)
if isempty(vcDir)
    flag = 0;
else
    S_dir = dir(vcDir);
    if isempty(S_dir)
        flag = 0;
    else
        flag = sum([S_dir.isdir]) > 0;
    end
%     flag = exist(vcDir, 'dir') == 7;
end
end %func


%--------------------------------------------------------------------------
% 8/2/17 JJJ: Documentation and test
function S = meta2struct_(vcFile)
% Convert text file to struct
S = struct();
if ~exist_file_(vcFile, 1), return; end

fid = fopen(vcFile, 'r');
mcFileMeta = textscan(fid, '%s%s', 'Delimiter', '=',  'ReturnOnError', false);
fclose(fid);
csName = mcFileMeta{1};
csValue = mcFileMeta{2};
for i=1:numel(csName)
    vcName1 = csName{i};
    if vcName1(1) == '~', vcName1(1) = []; end
    try         
        eval(sprintf('%s = ''%s'';', vcName1, csValue{i}));
        eval(sprintf('num = str2double(%s);', vcName1));
        if ~isnan(num)
            eval(sprintf('%s = num;', vcName1));
        end
        eval(sprintf('S = setfield(S, ''%s'', %s);', vcName1, vcName1));
    catch
        fprintf('%s = %s error\n', csName{i}, csValue{i});
    end
end
end %func


%--------------------------------------------------------------------------
% 7/21/2018 JJJ: rejecting directories, strictly search for flies
% 9/26/17 JJJ: Created and tested
function flag = exist_file_(vcFile, fVerbose)
if nargin<2, fVerbose = 0; end
if isempty(vcFile)
    flag = false; 
elseif iscell(vcFile)
    flag = cellfun(@(x)exist_file_(x, fVerbose), vcFile);
    return;
else
    S_dir = dir(vcFile);
    if numel(S_dir) == 1
        flag = ~S_dir.isdir;
    else
        flag = false;
    end
end
if fVerbose && ~flag
    fprintf(2, 'File does not exist: %s\n', vcFile);
end
end %func


%--------------------------------------------------------------------------
function [S_mda, fid_r] = readmda_header_(fname)
fid_r = fopen(fname,'rb');

try
    code=fread(fid_r,1,'int32');
catch
    error('Problem reading file: %s',fname);
end
if (code>0) 
    num_dims=code;
    code=-1;
    nBytes_sample = 4;
else
    nBytes_sample = fread(fid_r,1,'int32');
    num_dims=fread(fid_r,1,'int32');    
end
dim_type_str='int32';
if (num_dims<0)
    num_dims=-num_dims;
    dim_type_str='int64';
end

dimm=zeros(1,num_dims);
for j=1:num_dims
    dimm(j)=fread(fid_r,1,dim_type_str);
end

if (code==-1)
    vcDataType = 'single';
elseif (code==-2)
    vcDataType = 'uchar';
elseif (code==-3)
    vcDataType = 'single';
elseif (code==-4)
    vcDataType = 'int16';
elseif (code==-5)
    vcDataType = 'int32';
elseif (code==-6)
    vcDataType = 'uint16';
elseif (code==-7)
    vcDataType = 'double';
elseif (code==-8)
    vcDataType = 'uint32';
else
    vcDataType = ''; % unknown
end %if

S_mda = struct('dimm', dimm, 'vcDataType', vcDataType, ...
    'nBytes_header', ftell(fid_r), 'nBytes_sample', nBytes_sample);

if nargout<2, fclose(fid_r); end
end %func


%--------------------------------------------------------------------------
% 1/31/2019 JJJ: get the field(s) of a struct or index of an array or cell
function varargout = struct_get_(varargin)
    % same as struct_get_ function
    % retrieve a field. if not exist then return empty
    % [val1, val2] = get_(S, field1, field2, ...)
    % [val] = get_(cell, index)
    
    if nargin==0, varargout{1} = []; return; end
    S = varargin{1};
    if isempty(S), varargout{1} = []; return; end
    
    if isstruct(S)
        for i=2:nargin
            vcField = varargin{i};
            try
                varargout{i-1} = S.(vcField);
            catch
                varargout{i-1} = [];
            end
        end
    elseif iscell(S)
        try    
            varargout{1} = S{varargin{2:end}};
        catch
            varargout{1} = [];
        end
    else
        try    
            varargout{1} = S(varargin{2:end});
        catch
            varargout{1} = [];
        end
    end
    end %func


%--------------------------------------------------------------------------
function val = get_(S, vcName, def_val)
    % set a value if field does not exist (empty)
if nargin<3, def_val = []; end
if isempty(S), val = def_val; return; end
if ~isstruct(S)
    val = []; 
    fprintf(2, 'get_: %s must be a struct\n', inputname(1));
    return;
end
val = struct_get_(S, vcName);
if isempty(val), val = def_val; end
end %func