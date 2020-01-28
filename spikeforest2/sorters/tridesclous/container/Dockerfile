FROM nvidia/opencl

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
### Tridesclous
RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN pip install Cython
RUN pip install scipy numpy pandas scikit-learn matplotlib seaborn tqdm openpyxl PyQt5==5.14.0 pyqtgraph==0.10 quantities neo numba hdbscan
RUN pip install tridesclous==1.4.2

#########################################
## OpenCL/NVIDIA
RUN apt-get update && apt-get install -y opencl-headers ocl-icd-opencl-dev libclc-dev ocl-icd-libopencl1 clinfo
RUN pip install pyopencl

#########################################
# python packages
RUN pip install spikeextractors==0.7.1 spiketoolkit==0.5.1 spikesorters==0.2.2
RUN pip install kachery==0.4.6
