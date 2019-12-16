#!/bin/bash

if [[ -z "${KILOSORT2_PATH}" ]]; then
  echo "You must set the environment variable: KILOSORT2_PATH"
  exit -1
fi

thisdir=$PWD

cd $KILOSORT2_PATH/CUDA
matlab -nodisplay -nosplash -r "mexGPUall; quit"

cd "$thisdir"

mcc -m -v -R '-nodesktop, -nosplash -nojvm' \
  -a kilosort2_channelmap.m \
  -a kilosort2_config.m \
  -a constructNPYheader.m \
  -a writeNPY.m \
  kilosort2_master.m

cp kilosort2_master ../container/
