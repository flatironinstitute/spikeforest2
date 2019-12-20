FROM nvidia/cuda:10.1-base-ubuntu18.04

RUN apt-get update && apt-get install -y unzip
RUN apt-get install -y libxt-dev
RUN apt-get install -y curl 

RUN mkdir /install_matlab \
    && curl http://ssd.mathworks.com/supportfiles/downloads/R2019b/Release/1/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_R2019b_Update_1_glnxa64.zip > /install_matlab/MATLAB_Runtime_R2019b_Update_1_glnxa64.zip \
    && cd /install_matlab && unzip MATLAB_Runtime_R2019b_Update_1_glnxa64.zip && ./install -mode silent -agreeToLicense yes && cd / && rm -rf /install_matlab

ENV LD_LIBRARY_PATH /usr/local/MATLAB/MATLAB_Runtime/v97/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v97/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v97/sys/os/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v97/extern/bin/glnxa64

#########################################
### Python                                                               
RUN apt-get update && apt-get -y install git wget build-essential
RUN apt-get install -y python3 python3-pip
RUN ln -s python3 /usr/bin/python
RUN ln -s pip3 /usr/bin/pip
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3-tk

#########################################
### Numpy
RUN pip install numpy

#########################################
### Make sure we have python3 and a working locale
RUN rm /usr/bin/python && ln -s python3 /usr/bin/python && rm /usr/bin/pip && ln -s pip3 /usr/bin/pip
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
RUN apt-get install -y locales && locale-gen en_US.UTF-8

#########################################
### Compiled kilosort
### To generate (matlab compiler required):
###    See matlab/ directory
COPY kilosort_binary /kilosort_binary
RUN chmod a+x /kilosort_binary
ENV KILOSORT_BINARY_PATH=/kilosort_binary

# python packages
RUN pip install spikeextractors==0.7.0 spiketoolkit==0.5.0
RUN pip install spikesorters==0.2.2

RUN pip install kachery==0.4.6