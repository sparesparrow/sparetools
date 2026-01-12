# SpareTools MIA Consumer

Modular IoT Architecture - AI-orchestrated IoT platform integrated into the SpareTools ecosystem.

## Overview

This consumer package provides the MIA (Modular IoT Architecture) platform as part of the SpareTools monorepo. Following the OMS repository separation pattern, this package focuses on application-specific code while leveraging shared components from SpareTools foundation packages.

## Features

- **AI Orchestration**: Intelligent IoT device management and automation
- **MCP Integration**: Model Context Protocol for AI agent communication
- **Hardware Control**: GPIO, audio, and RF device management
- **Cloud Integration**: AWS and other cloud service connectivity
- **Self-Healing**: Automated system monitoring and remediation
- **OBD-II Simulation**: Vehicle diagnostics simulation
- **Voice Processing**: Speech-to-text and voice command processing

## Architecture

```
sparetools-mia (consumer)
├── Dependencies from SpareTools:
│   ├── sparetools-protocols/1.0.1 (FlatBuffers schemas)
│   ├── sparetools-embedded/1.0.0 (Embedded utilities)
│   ├── sparetools-test-harness/2.0.0 (Testing infrastructure)
│   └── sparetools-base/2.0.3 (Foundation utilities)
├── Application Code:
│   ├── src/mia/core/ - Core orchestration logic
│   ├── src/mia/hardware/ - Hardware device management
│   ├── src/mia/mcp/ - Model Context Protocol integration
│   ├── src/mia/services/ - IoT services and workers
│   └── src/mia/voice/ - Voice processing components
└── Testing:
    ├── test/integration/ - Integration tests
    └── src/mia/tests/ - Unit tests
```

## Core Components

### **Core Orchestrator**
```python
# Main orchestration logic
from mia.core import MIAOrchestrator

orchestrator = MIAOrchestrator()
orchestrator.start_device_discovery()
```

### **Hardware Management**
```python
# GPIO and device control
from mia.hardware.gpio_worker import GPIOWorker

gpio = GPIOWorker()
gpio.set_pin(18, True)  # Set GPIO pin 18 high
```

### **MCP Integration**
```python
# AI agent communication
from mia.mcp.orchestrator import MCPOrchestrator

mcp = MCPOrchestrator()
mcp.register_agent("voice_assistant")
```

### **OBD-II Services**
```python
# Vehicle diagnostics
from mia.services.obd_worker import OBDWorker

obd = OBDWorker()
diagnostics = obd.get_vehicle_status()
```

## Building and Installation

### **Python Package Installation**
```bash
# Install as Python package
pip install -e .
```

### **Conan-based Build**
```bash
# Using SpareTools ecosystem
conan install . --profile linux-release
conan build .

# Run tests
ctest
```

### **Docker Deployment**
```bash
# Using provided docker-compose
docker-compose -f src/mia/docker-compose.mcp.yml up
```

## Configuration

### **Environment Variables**
```bash
# AWS Configuration
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# MIA Configuration
export MIA_DEVICE_DISCOVERY_PORT=8080
export MIA_MCP_SERVER_PORT=3000
export MIA_REDIS_URL=redis://localhost:6379
```

### **Configuration Files**
- `orchestrator-config.yaml` - Main orchestration configuration
- `mia-config.json` - MIA-specific settings

## Testing

### **Unit Tests**
```bash
# Run unit tests
python -m pytest src/mia/tests/ -v
```

### **Integration Tests**
```bash
# Run integration tests
python -m pytest test/integration/ -v
```

### **Hardware Integration**
```bash
# Test with actual hardware
python test/integration/test_hardware_integration.py
```

## API Endpoints

### **REST API**
```
GET  /api/devices         - List connected devices
POST /api/devices/{id}    - Control specific device
GET  /api/status          - System status and health
POST /api/voice/command   - Voice command processing
```

### **WebSocket Streams**
- `/ws/devices` - Real-time device status updates
- `/ws/voice` - Voice processing results
- `/ws/diagnostics` - System diagnostics

## Hardware Support

### **Supported Devices**
- **Raspberry Pi** (3B+, 4, Zero W)
- **ESP32 Modules** (via NucleusESP32 integration)
- **Arduino Boards** (via serial communication)
- **OBD-II Adapters** (ELM327 compatible)

### **GPIO Pinouts**
```python
# Standard Raspberry Pi pin configuration
GPIO_PINS = {
    'led_status': 18,
    'button_reset': 23,
    'relay_control': 24,
    'sensor_power': 25
}
```

## Cloud Integration

### **AWS Services**
- **IoT Core**: Device management and messaging
- **Lambda**: Serverless function execution
- **DynamoDB**: Device state storage
- **S3**: Firmware and configuration storage

### **Integration Example**
```python
from mia.cloud_integration import AWSIoTClient

aws_client = AWSIoTClient()
aws_client.publish_device_status(device_id, status)
```

## Development Workflow

1. **Make Code Changes**: Edit files in consumer package
2. **Run Tests**: Use SpareTools testing infrastructure
3. **Build Package**: Use Conan for dependency management
4. **Version Updates**: Update versions in SpareTools central configuration

## Dependencies

### **Required SpareTools Packages**
- `sparetools-protocols/1.0.1` - Shared protocol schemas
- `sparetools-embedded/1.0.0` - Embedded system utilities
- `sparetools-test-harness/2.0.0` - Testing infrastructure
- `sparetools-base/2.0.3` - Foundation utilities

### **Python Dependencies**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `redis` - Caching and messaging
- `pyzmq` - ZeroMQ communication
- `torch` - Machine learning
- `librosa` - Audio processing

## Migration from Standalone Repository

This consumer package replaces the standalone `mia` repository integration, providing:

- **Dependency Management**: Uses SpareTools foundation packages
- **Shared Schemas**: FlatBuffers schemas from sparetools-protocols
- **CI/CD Integration**: Reusable workflows and templates
- **Consistency**: Follows OMS patterns across all projects

## Contributing

Follow the SpareTools contribution guidelines:

1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Submit pull request
5. CI/CD will validate changes across the ecosystem

## License

Apache 2.0