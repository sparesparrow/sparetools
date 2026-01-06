# SDR (Software Defined Radio) Tools

This directory contains tools for software-defined radio operations, signal analysis, and radio frequency monitoring.

## Directory Structure

```
sdr/
├── scripts/          # SDR control scripts
│   ├── sdr_device_info.py
│   ├── sdr_fm_radio.py
│   ├── sdr_scanner.py
│   ├── sdr_sdrplay_test.py
│   └── sdr_monitor.sh
├── examples/         # Example implementations
│   ├── sdrplay_flowgraph.py
│   └── sdrplay_gnuradio_example.py
├── services/         # System services
│   └── sdr-monitor.service
├── docs/             # Documentation
│   └── sdr_setup_guide.sh
└── README.md
```

## Components

### Device Management
- **Device Info**: SDR hardware detection and configuration
- **Setup Guide**: Installation and configuration instructions

### Radio Operations
- **FM Radio**: FM broadcast reception and decoding
- **Scanner**: Frequency scanning and signal detection
- **Monitor**: Continuous signal monitoring

### Examples
- **Flowgraphs**: GNU Radio Companion flowgraphs
- **Python Examples**: SDR programming examples

## Supported Hardware

- SDRplay RSP series
- RTL-SDR dongles
- HackRF One
- LimeSDR

## Software Dependencies

- GNU Radio
- SDRplay API
- SoapySDR
- Python libraries (numpy, scipy, matplotlib)

## Usage

### Check SDR Devices
```bash
python3 scripts/sdr_device_info.py
```

### FM Radio Reception
```bash
python3 scripts/sdr_fm_radio.py --frequency 88.5
```

### Frequency Scanning
```bash
python3 scripts/sdr_scanner.py --start 88 --end 108 --step 0.1
```

### Start Monitoring Service
```bash
sudo systemctl start sdr-monitor.service
```

## Frequency Ranges

- **FM Broadcast**: 88-108 MHz
- **AM Broadcast**: 535-1605 kHz
- **Airband**: 118-137 MHz
- **ISM Bands**: 433 MHz, 868 MHz, 2.4 GHz

## Applications

- Radio frequency monitoring
- Signal intelligence
- Spectrum analysis
- Amateur radio operations
- Wireless protocol analysis