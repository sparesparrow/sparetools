# WiFi Sensing Research Environment
# Supports CSI extraction, signal processing, and machine learning for WiFi sensing research

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Core system tools
    build-essential \
    cmake \
    git \
    wget \
    curl \
    unzip \
    pkg-config \
    software-properties-common \
    # Python and development tools
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    # WiFi and networking tools
    wireless-tools \
    iw \
    tcpdump \
    aircrack-ng \
    rfkill \
    # Signal processing libraries
    libfftw3-dev \
    libgsl-dev \
    liblapack-dev \
    libblas-dev \
    # Computer vision and plotting (for visualization)
    libopencv-dev \
    python3-opencv \
    # Audio processing (for TTS and signal analysis)
    libasound2-dev \
    portaudio19-dev \
    libsndfile1-dev \
    # GUI and display (for matplotlib and interactive plots)
    libgtk-3-dev \
    libgdk-pixbuf2.0-dev \
    libcairo-gobject2 \
    libpango1.0-dev \
    libatk1.0-dev \
    libcairo-gobject2 \
    libgtk-3-0 \
    # LaTeX for matplotlib text rendering
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-extra-utils \
    texlive-latex-extra \
    # SDR tools (for advanced RF sensing)
    rtl-sdr \
    libusb-1.0-0-dev \
    libuhd-dev \
    uhd-host \
    # Additional development libraries
    libboost-all-dev \
    libeigen3-dev \
    libhdf5-dev \
    libyaml-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages in stages for better caching
# Core scientific computing
RUN pip3 install --no-cache-dir \
    numpy \
    scipy \
    matplotlib \
    pandas \
    scikit-learn \
    jupyter \
    jupyterlab \
    notebook

# Signal processing and communications
RUN pip3 install --no-cache-dir \
    scikit-signal \
    pyfftw \
    spectrum \
    pyserial \
    pyvisa

# Machine learning and deep learning
RUN pip3 install --no-cache-dir \
    tensorflow \
    torch \
    torchvision \
    torchaudio \
    scikit-learn \
    xgboost \
    lightgbm \
    catboost

# Computer vision and image processing
RUN pip3 install --no-cache-dir \
    opencv-python \
    pillow \
    scikit-image \
    albumentations

# Audio processing and TTS
RUN pip3 install --no-cache-dir \
    librosa \
    soundfile \
    pyaudio \
    pyttsx3 \
    gtts \
    pygame

# Networking and wireless
RUN pip3 install --no-cache-dir \
    scapy \
    netifaces \
    wifi \
    pyroute2

# SDR and RF processing
RUN pip3 install --no-cache-dir \
    pyrtlsdr \
    soapysdr \
    SoapyRTLSDR

# Data processing and visualization
RUN pip3 install --no-cache-dir \
    seaborn \
    plotly \
    bokeh \
    altair \
    holoviews \
    hvplot \
    panel

# Development and testing tools
RUN pip3 install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-xdist \
    black \
    flake8 \
    mypy \
    pre-commit \
    ipdb \
    tqdm

# Web development (for dashboards and interfaces)
RUN pip3 install --no-cache-dir \
    flask \
    fastapi \
    uvicorn \
    streamlit \
    dash \
    gradio \
    jupyter-server-proxy

# CSI-specific tools and libraries
RUN pip3 install --no-cache-dir \
    h5py \
    pyarrow \
    feather-format \
    tables

# Install additional CSI tools from source
WORKDIR /tmp
RUN git clone https://github.com/dhalperi/linux-80211n-csitool.git && \
    cd linux-80211n-csitool && \
    make && \
    make install && \
    cd .. && rm -rf linux-80211n-csitool

# Install Atheros CSI tool if available
RUN git clone https://github.com/xieyaxiongfly/Atheros-CSI-Tool.git && \
    cd Atheros-CSI-Tool && \
    chmod +x setup.sh && \
    ./setup.sh && \
    cd .. && rm -rf Atheros-CSI-Tool || true

# Set up Jupyter environment
RUN jupyter labextension install jupyterlab-plotly && \
    jupyter nbextension enable --py --sys-prefix widgetsnbextension

# Create workspace directories
RUN mkdir -p /workspace/{docs,research/{papers,repositories},src/{core,analysis,visualization,tools},docker,scripts,tests,notebooks,data/{raw,processed,models}}

# Set working directory
WORKDIR /workspace

# Create non-root user for development
RUN useradd -m -s /bin/bash wifi-research && \
    chown -R wifi-research:wifi-research /workspace

# Copy requirements and setup files
COPY docker/requirements.txt /workspace/docker/
COPY docker/setup.sh /workspace/docker/

# Install additional Python requirements
RUN pip3 install --no-cache-dir -r docker/requirements.txt || true

# Set up the environment
RUN chmod +x docker/setup.sh && \
    ./docker/setup.sh

# Expose ports for Jupyter, web interfaces, and development
EXPOSE 8888 5000 8000 8501 8050

# Set default user
USER wifi-research

# Default command
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]