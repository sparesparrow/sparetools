# ESP32 Development Environment
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    cmake \
    ninja-build \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --upgrade pip
RUN pip3 install conan platformio

# Install ESP32 toolchain
RUN wget https://dl.espressif.com/dl/xtensa-esp32-elf-linux64-1.22.0-97-gc752ad5-5.2.0.tar.gz \
    && tar -xzf xtensa-esp32-elf-linux64-1.22.0-97-gc752ad5-5.2.0.tar.gz \
    && mv xtensa-esp32-elf /opt/xtensa-esp32-elf \
    && rm xtensa-esp32-elf-linux64-1.22.0-97-gc752ad5-5.2.0.tar.gz

# Add ESP32 toolchain to PATH
ENV PATH="/opt/xtensa-esp32-elf/bin:${PATH}"

# Setup Conan
RUN conan profile new default --detect
RUN conan remote add sparesparrow https://conan.cloudsmith.io/sparesparrow/

# Create workspace directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]