# Start with an image that includes ITK-SNAP command-line tools
FROM ibmcom/powerai:1.6.2-pytorch-ubuntu18.04-py37

# Standard stuff
RUN sudo apt-get update
RUN sudo apt-get install -y git-core curl

# Working directory
WORKDIR /service

# Install the neck cutting script and service script
COPY . /service/

