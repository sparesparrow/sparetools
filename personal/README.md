# Personal Tools & Configurations

This directory contains personal scripts, configurations, and projects that are valuable to preserve and share.

## Directory Structure

```
personal/
├── scripts/              # Personal utility scripts
│   └── mount-dev.sh     # Device mounting utilities
├── configs/              # Configuration files
│   └── diagram_configs.json  # Diagram generation configs
├── examples/             # Example code and usage patterns
│   ├── example_usage.py  # General usage examples
│   └── prompt_examples.py # Prompt system examples
└── projects/             # Standalone projects
    └── network_monitor/  # Complete network monitoring system
```

## Network Monitor Project

The `network_monitor/` directory contains a comprehensive network monitoring and management system with:

### Features
- **Device Discovery**: Automatic network device detection and monitoring
- **Threat Assessment**: Real-time security monitoring and alerting
- **Service Management**: Systemd service integration
- **Screen Casting**: RTSP streaming and continuous casting capabilities
- **KDE Connect Integration**: Mobile device connectivity
- **WiFi Hotspot**: Automated hotspot management

### Components
- **Core Scripts**: Network monitoring, device discovery, threat assessment
- **Services**: Systemd service files for automated operation
- **Modules**: Specialized monitoring modules (SSH, Docker, SDR, etc.)
- **Configuration**: Flexible configuration system
- **Data Storage**: SQLite databases for device tracking and topology
- **Logging**: Comprehensive logging and alerting system

### Usage
See `network_monitor/README.md` for detailed setup and usage instructions.

## Personal Scripts

The `scripts/` directory contains utility scripts for:
- Device mounting and management
- Development environment setup
- System administration tasks

## Configuration Files

The `configs/` directory contains configuration files for:
- Diagram generation tools
- Development environment settings
- Tool-specific configurations

## Examples

The `examples/` directory contains example code demonstrating:
- API usage patterns
- Prompt system integration
- Best practices for various tools

## Integration with Sparetools

These personal tools integrate with the broader sparetools ecosystem:
- Network monitor uses sparetools networking components
- Scripts may reference sparetools packages
- Configurations can be used with sparetools tools

## Backup & Preservation

This directory serves as a backup of valuable personal configurations and tools that:
- Are not part of the main sparetools packages
- Contain customizations and personal workflows
- May be useful for setting up new environments
- Preserve institutional knowledge and automation

## Maintenance

When adding new content to this directory:
1. Ensure it's valuable and reusable
2. Add appropriate documentation
3. Consider if it should be moved to a dedicated sparetools package
4. Update this README as needed