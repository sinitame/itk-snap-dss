# Use official Python as parent image
FROM python:2.7-slim

# Install dependancies
RUN apt-get update && \
    apt-get install -y git-core curl gcc libpq-dev python-dev

# Create workdir
WORKDIR /app

# Checkout the server 
COPY . /app

# Install the python dependencies
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run server on port 80887650
CMD python -u /app/app.py --server
