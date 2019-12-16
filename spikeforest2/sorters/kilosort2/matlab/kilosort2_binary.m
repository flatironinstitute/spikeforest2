function kilosort2_binary(dat_file, output_dir, params_path)

try
    kilosort2_master(dat_file, output_dir, params_path)
catch
    fprintf('----------------------------------------');
    fprintf(lasterr());
    quit(1);
end
quit(0);