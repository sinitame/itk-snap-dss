# Use official Python as parent image
FROM python:3.7

# Make sure we have git
RUN apt-get update
RUN apt-get install -y git-core curl python-dev

# Create workdir
WORKDIR /deamons

# Checkout the server 
COPY . /deamons

# Install the python dependencies
RUN pip install flask flask_restful requests

# Run server
CMD python -u /deamons/deamon_1.py
