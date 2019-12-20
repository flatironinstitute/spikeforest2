#!/bin/bash

thisdir=$PWD

git clone https://github.com/cortex-lab/KiloSort KiloSort
cd KiloSort && git checkout cd040da1963dd760da98b54c811b3fd441d54e79 && cd ..
KILOSORT_PATH=$PWD/KiloSort

cd $KILOSORT_PATH/CUDA
matlab -nodisplay -nosplash -r "mexGPUall; quit"

cd "$thisdir"

### TODO: fix this
mcc -m -v -R '-nodesktop, -nosplash -nojvm' \
  -a kilosort_master.m \
  -a kilosort_channelmap.m \
  -a kilosort_config.m \
  -a constructNPYheader.m \
  -a writeNPY.m \
  -a $KILOSORT_PATH \
  kilosort_binary.m

cp kilosort_binary ../container/
