# Start with an image that includes ITK-SNAP command-line tools
FROM ibmcom/powerai:1.6.2-pytorch-ubuntu18.04-py37

# Standard stuff
RUN sudo apt-get update
RUN sudo apt-get install -y git-core curl

# Working directory
WORKDIR /service

# Install the neck cutting script and service script
COPY . /service/

RUN /opt/anaconda/bin/pip install /service/SimpleITK-1.2.0+gd6026-cp37-cp37m-linux_ppc64le.whl
RUN /opt/anaconda/bin/pip install pynrrd

CMD python -u /service/deamon.py

