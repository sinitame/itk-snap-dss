# Use official Python as parent image
FROM python:3.7

# Create workdir
WORKDIR /deamons

# Checkout the server 
COPY . /deamons

# Install the python dependencies
RUN pip install requests

# Run server
CMD python -u /deamons/master_deamon.py
