ARG BASE_IMAGE=ubuntu:22.04
FROM $BASE_IMAGE
ENV DEBIAN_FRONTEND noninteractive

FROM python:3.8-bullseye
WORKDIR /app
RUN pip install pyopengl
RUN pip install pyglet==1.5.15
RUN pip install pyyaml

RUN set -eux && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libgtk-3-dev && \
        # https://github.com/pyenv/pyenv/wiki#suggested-build-environment
    apt-get install -y \
        xvfb \
        make \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        wget \
        curl \
        llvm \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libffi-dev \
        liblzma-dev \
        git && \
    # Psychopy Dependencies
    apt-get install -y \
        libhdf5-dev \
        freeglut3-dev \
        libwebkitgtk-1.0 \
        libusb-1.0-0-dev \
        portaudio19-dev \
        libasound2-dev \
        libsndfile1-dev \
        libportmidi-dev \
        liblo-dev && \
    # General User Tools
    apt-get install -y gosu
RUN pip install attrdict3
RUN pip install wxPython
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD [ "xvfb-run", "-s", "-screen 0 1366x768x24 -ac +extension GLX +render -noreset", "python", "scripts/oz-speller_without-headset.py" ]