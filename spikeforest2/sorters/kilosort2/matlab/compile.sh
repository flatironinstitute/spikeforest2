#!/bin/bash

# if [[ -z "${KILOSORT2_PATH}" ]]; then
#   echo "You must set the environment variable: KILOSORT2_PATH"
#   exit -1
# fi

thisdir=$PWD

# git clone https://github.com/alexmorley/Kilosort2
git clone https://github.com/MouseLand/Kilosort2 Kilosort2
cd Kilosort2 && git checkout 67a42a87b866b6150385a46eec358adb349d9ff2 && cd ..
KILOSORT2_PATH=$PWD/Kilosort2

cd $KILOSORT2_PATH/CUDA
matlab -nodisplay -nosplash -r "mexGPUall; quit"

cd "$thisdir"

mcc -m -v -R '-nodesktop, -nosplash -nojvm' \
  -a kilosort2_master.m \
  -a kilosort2_channelmap.m \
  -a kilosort2_config.m \
  -a constructNPYheader.m \
  -a writeNPY.m \
  -a $KILOSORT2_PATH \
  kilosort2_binary.m

cp kilosort2_binary ../container/
