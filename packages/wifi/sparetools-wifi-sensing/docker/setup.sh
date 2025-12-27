#!/bin/bash

# WiFi Sensing Research Environment Setup Script
# This script configures the Docker environment for WiFi sensing research

set -e

echo "🚀 Setting up WiFi Sensing Research Environment..."

# Create necessary directories
mkdir -p /workspace/{docs,research/{papers,repositories},src/{core,analysis,visualization,tools},docker,scripts,tests,notebooks,data/{raw,processed,models},logs}

# Set up Python path
export PYTHONPATH="/workspace/src:$PYTHONPATH"

# Install additional system packages if needed
if [ -f "/workspace/docker/system-requirements.txt" ]; then
    echo "📦 Installing additional system packages..."
    xargs -a /workspace/docker/system-requirements.txt apt-get install -y --no-install-recommends
fi

# Install CSI tools if hardware is available
echo "🔧 Checking for CSI-capable hardware..."
if lsusb | grep -q "Intel.*5300\|Atheros.*9\|Broadcom"; then
    echo "✅ CSI-capable WiFi hardware detected"
    echo "CSI_HARDWARE_AVAILABLE=1" >> /workspace/.env
else
    echo "⚠️  No CSI-capable hardware detected (Intel 5300/Atheros/Broadcom)"
    echo "CSI_HARDWARE_AVAILABLE=0" >> /workspace/.env
fi

# Set up Jupyter configuration
mkdir -p /root/.jupyter
cat > /root/.jupyter/jupyter_notebook_config.py << EOF
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False
c.NotebookApp.allow_root = True
c.NotebookApp.notebook_dir = '/workspace'
c.NotebookApp.token = ''
c.NotebookApp.password = ''
EOF

# Configure matplotlib backend for headless operation
mkdir -p /root/.config/matplotlib
echo "backend: Agg" > /root/.config/matplotlib/matplotlibrc

# Set up git configuration template
git config --global init.defaultBranch main
git config --global user.name "WiFi Sensing Researcher"
git config --global user.email "research@wifi-sensing.local"

# Create environment file
cat > /workspace/.env << EOF
# WiFi Sensing Research Environment Configuration
WORKSPACE_ROOT=/workspace
PYTHONPATH=/workspace/src
CSI_HARDWARE_AVAILABLE=0
JUPYTER_PORT=8888
STREAMLIT_PORT=8501
DASH_PORT=8050
FLASK_PORT=5000

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
TORCH_USE_CUDA_DSA=1

# Development settings
DEBUG=1
LOG_LEVEL=INFO
EOF

# Set up logging
mkdir -p /workspace/logs
touch /workspace/logs/setup.log

echo "$(date): Environment setup completed" >> /workspace/logs/setup.log

# Create initial directory structure documentation
cat > /workspace/docs/DIRECTORY_STRUCTURE.md << 'EOF'
# WiFi Sensing Workspace Directory Structure

```
/workspace/
├── docs/                    # Documentation and research notes
│   ├── RESEARCH_PLAN.md    # Comprehensive research plan
│   └── DIRECTORY_STRUCTURE.md
├── research/               # Research materials
│   ├── papers/            # Downloaded research papers
│   └── repositories/      # Cloned GitHub repositories
├── src/                   # Source code
│   ├── core/             # Core WiFi sensing algorithms
│   ├── analysis/         # Data analysis and processing
│   ├── visualization/    # Plotting and visualization tools
│   └── tools/            # Utility scripts and tools
├── docker/               # Container configuration
├── scripts/              # Research and automation scripts
├── tests/                # Unit tests and integration tests
├── notebooks/            # Jupyter notebooks for experiments
├── data/                 # Datasets and experimental data
│   ├── raw/             # Raw CSI data and measurements
│   ├── processed/       # Processed and cleaned data
│   └── models/          # Trained machine learning models
└── logs/                # Application logs
```
EOF

echo "✅ WiFi Sensing Research Environment Setup Complete!"
echo ""
echo "🎯 Quick Start:"
echo "  jupyter lab --ip=0.0.0.0 --port=8888"
echo "  streamlit run src/demo/app.py"
echo ""
echo "📚 Documentation: /workspace/docs/"
echo "🔬 Research: /workspace/research/"
echo "💻 Code: /workspace/src/"