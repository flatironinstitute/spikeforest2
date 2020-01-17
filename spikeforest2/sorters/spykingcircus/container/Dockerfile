FROM ubuntu:18.04

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

# Install SpyKING CIRCUS
RUN apt-get update && apt-get install -y libmpich-dev
RUN pip install pyqt5==5.13
RUN apt-get update && apt-get install -y qt5-default
RUN apt-get update && apt-get install -y libglib2.0-0 libgl1-mesa-glx
RUN apt-get update && apt-get install -y packagekit-gtk3-module libcanberra-gtk-module libcanberra-gtk3-module
RUN pip install cmake scikit-build
RUN pip install spyking-circus==0.9.0

# python packages
RUN pip install spikeextractors==0.7.1 spiketoolkit==0.5.1 spikesorters==0.2.2
RUN pip install kachery==0.4.4