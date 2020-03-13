# Start with an image that includes ITK-SNAP command-line tools
FROM ibmcom/powerai:1.6.2-pytorch-ubuntu18.04-py37

USER 2051

# Standard stuff
RUN sudo apt-get update
RUN sudo apt-get install -y git-core curl\
                            build-essential \
                            cmake \
                            htop \
                            zip \
                            unzip

# Working directory
WORKDIR /service

# Install the neck cutting script and service script
COPY . /service/

RUN /opt/anaconda/envs/wmlce/bin/pip install /service/SimpleITK-1.2.0+gd6026-cp37-cp37m-linux_ppc64le.whl
RUN /opt/anaconda/envs/wmlce/bin/pip install pynrrd

CMD /opt/anaconda/envs/wmlce/bin/python -u /service/deamon.py

