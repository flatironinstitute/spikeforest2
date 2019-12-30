#!/bin/bash

thisdir=$PWD

git clone https://github.com/JaneliaSciComp/JRCLUST JRCLUST
cd JRCLUST && git checkout 3d2e75c0041dca2a9f273598750c6a14dbc4c1b8 && cd ..
JRCLUST_PATH=$PWD/JRCLUST

cd "$thisdir"

# replace a buggy file

cd JRCLUST
matlab -nodisplay -nosplash -r "jrclust.CUDA.compileCUDA(); quit;"

cd "$thisdir"
cp exportFiringRate.m $JRCLUST_PATH/+jrclust/+curate/@CurateController/exportFiringRate.m
mcc -m -v -R '-nodesktop, -nosplash -nojvm' \
  -a writemda.m \
  -a $JRCLUST_PATH \
  jrclust_binary.m

cp jrclust_binary ../container/
