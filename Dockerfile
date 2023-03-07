# syntax=docker/dockerfile:1

# Python 3.9.9 Debian Buster Linux Base
FROM python:3.9.9-buster

# Set Labels  
LABEL authors="Zexin Li, Jackrite To, Dhwani Solanki, Justus Bisten, Sanjana Srinivasan"
LABEL emails="s0zeliiii@uni-bonn.de, s0j.tooo@uni-bonn.de, s0dhsola@uni-bonn.de, s6jubist@uni-bonn.de, s0sasrin@uni-bonn.de"
LABEL version="0.1.0"

# Set working directory
WORKDIR /usr/src/authormaps

# Copy frontend and package files to working directory
COPY  ./ ./

# Install my python application
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir python-dotenv && \
    pip install --no-cache-dir ./authormaps_pkg/

# Define FLASK_PORT to be 8080 by default and choosable as optional build-argument
ARG FLASK_PORT=8080
ENV FLASK_PORT=${FLASK_PORT}

# Expose port FLASK_PORT
EXPOSE ${FLASK_PORT}/tcp

# Start the web-based user interface on localhost
ENTRYPOINT ["python","./authormaps_frontend/run.py"]
