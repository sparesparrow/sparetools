FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ninja-build \
        cmake \
        perl \
        git \
        curl \
        unzip \
        pkg-config \
        python3 \
        python3-venv \
        python3-pip \
        python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir \
        conan==2.21.0 \
        black \
        flake8 \
        isort

ENV PATH="/root/.local/bin:${PATH}"

