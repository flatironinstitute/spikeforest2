#!/bin/bash

# if [[ -z "${JRCLUST_PATH}" ]]; then
#   echo "You must set the environment variable: JRCLUST_PATH"
#   exit -1
# fi

thisdir=$PWD

git clone https://github.com/JaneliaSciComp/JRCLUST JRCLUST
cd JRCLUST && git checkout 3d2e75c0041dca2a9f273598750c6a14dbc4c1b8 && cd ..
JRCLUST_PATH=$PWD/JRCLUST

cd $JRCLUST_PATH

# replace a buggy file

matlab -nodisplay -nosplash -r "jrclust.CUDA.compileCUDA(); quit;"

cd "$thisdir"
cp exportFiringRate.m $JRCLUST_PATH/+jrclust/+curate/@CurateController/exportFiringRate.m
mcc -m -v -R '-nodesktop, -nosplash -nojvm' \
  -a jrclust_master.m \
  -a $JRCLUST_PATH \
  jrclust_binary.m

cp jrclust_binary ../container/
