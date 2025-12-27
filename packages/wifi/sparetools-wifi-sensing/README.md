# WiFi Sensing Research Workspace

A comprehensive research environment for WiFi sensing, Channel State Information (CSI) analysis, and motion detection through walls using advanced signal processing and machine learning techniques.

## 🎯 Overview

This workspace provides everything needed to research and implement WiFi sensing technologies that can detect human movement, activity recognition, and other sensing applications using standard WiFi hardware and CSI (Channel State Information) data.

### Key Features
- **CSI Extraction**: Tools for extracting Channel State Information from various WiFi chipsets
- **Motion Detection**: Algorithms for detecting movement through walls and obstacles
- **Activity Recognition**: Machine learning models for classifying human activities
- **Research Papers**: Curated collection of key research papers on WiFi sensing
- **Code Repositories**: Cloned research implementations and tools
- **Containerized Environment**: Docker setup for reproducible research

## 📁 Project Structure

```
wifi-sensing-workspace/
├── docs/                          # Documentation and research notes
│   ├── RESEARCH_PLAN.md          # Comprehensive research plan
│   └── DIRECTORY_STRUCTURE.md    # Directory structure guide
├── research/                      # Research materials
│   ├── papers/                   # Downloaded research papers (11 papers)
│   │   ├── bibliography.md       # Paper bibliography and references
│   │   └── *.pdf                 # Research papers
│   └── repositories/             # Cloned GitHub repositories
│       ├── nexmon_csi/           # Broadcom CSI extraction
│       ├── Wifi_Activity_Recognition/  # Activity recognition framework
│       └── repositories.md       # Repository index
├── src/                          # Source code
│   ├── core/                     # Core WiFi sensing algorithms
│   ├── analysis/                 # Data analysis and processing
│   ├── visualization/            # Plotting and visualization tools
│   └── tools/                    # Utility scripts and tools
├── docker/                       # Container configuration
│   ├── Dockerfile                # Main container definition
│   ├── docker-compose.yml        # Multi-service orchestration
│   ├── requirements.txt          # Additional Python packages
│   └── setup.sh                  # Container initialization
├── scripts/                      # Research and automation scripts
│   ├── download_papers.py        # Paper download script
│   └── clone_repositories.py     # Repository cloning script
├── notebooks/                    # Jupyter notebooks for experiments
├── tests/                        # Unit tests and integration tests
├── data/                         # Datasets and experimental data
│   ├── raw/                      # Raw CSI data and measurements
│   ├── processed/                # Processed and cleaned data
│   └── models/                   # Trained machine learning models
└── logs/                         # Application logs
```

## 🔄 Flipper Zero Integration

**NEW**: This workspace now includes integration with the Flipper Zero DIY project for advanced WiFi sensing and wardriving capabilities.

### Flipper Zero Features
- **DIY Multi-tool**: Portable device for wireless protocols
- **WiFi Capabilities**: ESP32-S2 development board support
- **Wardriving**: Mobile WiFi mapping with GPS
- **Unified Build System**: Combined firmware and analysis tools

### Integration Components
- **Flipper Zero Repository**: `research/repositories/flipper_zero/`
- **Unified Build Scripts**: Automated integration builds
- **WiGLE Tools Integration**: Data analysis and visualization
- **Hardware Guides**: Complete setup documentation

📖 **Integration Guide**: [docs/FLIPPER_ZERO_INTEGRATION.md](docs/FLIPPER_ZERO_INTEGRATION.md)

### Quick Flipper Setup
```bash
# Build the integrated suite
cd research/repositories/flipper_zero/wifi_sensing_integration
python3 scripts/unified_build.py

# Run the integration
bash build_output/scripts/run_integration.sh
```

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Build and run the development environment:**
   ```bash
   cd wifi-sensing-workspace
   docker-compose up wifi-sensing-research
   ```

2. **Access Jupyter Lab:**
   - Open http://localhost:8888 in your browser
   - No token required (configured for development)

3. **Alternative services:**
   ```bash
   # Development environment
   docker-compose up wifi-sensing-dev

   # Analysis environment with GPU support
   docker-compose up wifi-sensing-analysis

   # Demo environment with web interface
   docker-compose up wifi-sensing-demo
   ```

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r docker/requirements.txt
   ```

2. **Set up the environment:**
   ```bash
   export PYTHONPATH="$PWD/src:$PYTHONPATH"
   ```

3. **Run basic WiFi scanning:**
   ```bash
   python3 src/tools/wifi_scanner.py
   ```

## 📚 Research Papers

The workspace includes **11 key research papers** on WiFi sensing and CSI:

### Foundational Papers
- **CSI-based Device-free Localization** - Wu et al. (2013)
- **Decimeter-Level Localization** - Xiao et al. (2016)

### Activity Recognition
- **WiFall: Device-free Fall Detection** - Wang et al. (2017)
- **Deep Learning for CSI** - Wang et al. (2018)

### Advanced Techniques
- **Multi-person Localization** - Zou et al. (2019)
- **Cross-Environment Adaptation** - Ma et al. (2020)

### Surveys and Reviews
- **WiFi Sensing Survey** - Ma et al. (2019)
- **CSI-based Sensing Survey** - Li et al. (2020)

### Privacy & Recent Advances
- **Privacy-Preserving Sensing** - Chen et al. (2021)
- **Transformer-based CSI Sensing** - Yang et al. (2022)
- **Multi-modal WiFi Sensing** - Zhang et al. (2023)

📖 **Full bibliography**: [research/papers/bibliography.md](research/papers/bibliography.md)

## 🛠️ Cloned Repositories

Successfully cloned research repositories:

### CSI Tools & Frameworks
- **[nexmon_csi](research/repositories/nexmon_csi/)**: Broadcom CSI extraction for Raspberry Pi and other devices
- **Wifi_Activity_Recognition**: WiFi-based activity recognition framework

### Repository Index
📋 **Complete repository list**: [research/repositories/repositories.md](research/repositories/repositories.md)

## 🔬 Core Components

### CSI Extraction Tools

#### Intel 5300 CSI Tool
```bash
# Build and install
cd research/repositories/linux-80211n-csitool
make
sudo make install
```

#### Nexmon CSI (Broadcom)
```bash
# For Raspberry Pi and Broadcom chipsets
cd research/repositories/nexmon_csi
make
sudo make install
```

### WiFi Sensing Algorithms

#### Basic Motion Detection
```python
from src.core.motion_detector import MotionDetector

detector = MotionDetector()
motion_detected = detector.analyze_signal_fluctuations(csi_data)
```

#### Activity Recognition
```python
from src.analysis.activity_classifier import ActivityClassifier

classifier = ActivityClassifier()
activities = ['walking', 'running', 'sitting', 'standing']
predictions = classifier.predict(csi_data, activities)
```

## 🧪 Experiments & Examples

### Jupyter Notebooks
- `notebooks/csi_analysis.ipynb` - CSI data analysis and visualization
- `notebooks/motion_detection.ipynb` - Motion detection algorithms
- `notebooks/activity_recognition.ipynb` - Activity classification models

### Demo Scripts
```bash
# WiFi network scanning with motion detection
python3 src/tools/wifi_scanner.py --motion-detection

# CSI data collection
python3 src/tools/csi_collector.py --interface wlan0

# Real-time visualization
python3 src/visualization/realtime_plot.py
```

## 🔧 Hardware Requirements

### Supported WiFi Hardware
- **Intel 5300**: Most widely supported for CSI extraction
- **Atheros AR9580/AR9590**: Alternative chipset support
- **Broadcom BCM4352**: Mobile device CSI extraction
- **Raspberry Pi**: With nexmon for CSI extraction

### System Requirements
- **OS**: Linux (Ubuntu 18.04+ recommended)
- **WiFi Standards**: 802.11n/ac/ax support
- **Memory**: 8GB+ RAM for data processing
- **Storage**: 100GB+ for datasets and models
- **GPU**: NVIDIA GPU recommended for deep learning

## 📊 Data & Models

### Public Datasets
- **WiAR Dataset**: Activity recognition dataset
- **SignFi Dataset**: Sign language recognition
- **WidAR Dataset**: Multi-person localization

### Model Zoo
Pre-trained models for:
- Activity classification
- Motion detection
- Localization tasks

## 🤝 Contributing

### Research Areas
1. **Algorithm Development**: New CSI processing techniques
2. **Hardware Support**: Additional chipset support
3. **Application Domains**: Novel sensing applications
4. **Privacy Enhancement**: Privacy-preserving sensing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This research workspace is provided for educational and research purposes. Individual components may have their own licenses - please check the respective repositories and papers.

## 🔗 Related Resources

### Academic Groups
- **UCSD WiFi Sensing**: University of California San Diego
- **MIT CSAIL**: Computer Science and Artificial Intelligence Laboratory
- **CMU RI**: Carnegie Mellon University Robotics Institute

### Industry Research
- **Microsoft Research**: WiFi sensing projects
- **Google AI**: RF sensing initiatives
- **Intel Labs**: Wireless sensing research

## 📞 Support & Contact

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the research plan: [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)
- Review the FAQ in documentation

---

## 🎯 Research Impact

WiFi sensing represents a paradigm shift in ubiquitous computing, enabling:
- **Privacy-preserving monitoring** without cameras
- **Structural health monitoring** through existing infrastructure
- **Smart home automation** with implicit sensing
- **Healthcare applications** for elderly care and rehabilitation
- **Security systems** for intrusion detection

This workspace provides the foundation for advancing this exciting field of research.

---

*WiFi Sensing Research Workspace v1.0*
*Created: 2025-01-24*