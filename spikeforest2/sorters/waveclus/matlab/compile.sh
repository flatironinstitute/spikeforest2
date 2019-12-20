#!/bin/bash

thisdir=$PWD

# git clone https://github.com/alexmorley/Kilosort2
git clone https://github.com/csn-le/wave_clus.git wave_clus
cd wave_clus && git checkout cb8db518f915b38ddd73342d8b0688f3f5bb0c07 && cd ..
WAVECLUS_PATH=$PWD/wave_clus

cd "$thisdir"

echo $PWD
mcc -m -v -R '-nodesktop, -nosplash -nojvm' \
  -a set_parameters_spf.m \
  -a readmda.m \
  -a writemda.m \
  -a $WAVECLUS_PATH \
  waveclus_binary.m

cp waveclus_binary ../container/
