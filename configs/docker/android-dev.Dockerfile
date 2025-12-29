# Android Development Environment
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    python3 \
    python3-pip \
    git \
    cmake \
    ninja-build \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --upgrade pip
RUN pip3 install conan

# Install Android SDK
RUN wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip \
    && unzip commandlinetools-linux-8512546_latest.zip \
    && mkdir -p /opt/android-sdk/cmdline-tools \
    && mv cmdline-tools /opt/android-sdk/cmdline-tools/latest \
    && rm commandlinetools-linux-8512546_latest.zip

# Add Android SDK to PATH
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${PATH}"

# Accept Android SDK licenses
RUN yes | sdkmanager --licenses

# Install Android SDK components
RUN sdkmanager "platform-tools" "platforms;android-28" "build-tools;30.0.3"

# Setup Conan
RUN conan profile new default --detect
RUN conan remote add sparesparrow https://conan.cloudsmith.io/sparesparrow/

# Create workspace directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]