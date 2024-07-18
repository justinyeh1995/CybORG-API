# Set Ubuntu and Python versions from pre-built images
FROM ubuntu:22.10
FROM python:3.10.0

# Set working directory to /cage
WORKDIR /cage

# Copy local package requirements and init script into container's /cage folder
COPY . /cage

WORKDIR /cage/api/v1/CybORG

# Install packages
RUN pip install -e .

WORKDIR /cage

# Install packages
RUN pip install -r requirements.txt