# Real-Time Screen Streaming Solutions

This workspace contains three comprehensive approaches to real-time screen streaming for CTF challenges, each optimized for different use cases and requirements.

## 🎯 Solutions Overview

### 1. RTSP Streaming (`rtsp_streaming/`)
- **Protocol**: RTSP (Real-Time Streaming Protocol)
- **Latency**: < 2 seconds (true real-time)
- **Best for**: True real-time requirements, surveillance systems
- **TV Support**: Requires RTSP client support

### 2. HLS Streaming (`hls_streaming/`)
- **Protocol**: HLS (HTTP Live Streaming)
- **Latency**: 3-10 seconds (inherent HLS latency)
- **Best for**: Web compatibility, adaptive bitrate
- **TV Support**: Requires HLS client support

### 3. Continuous File Streaming (`continuous_file_streaming/`)
- **Protocol**: DLNA/UPnP with continuous file updates
- **Latency**: 5-15 seconds (file processing + DLNA rescan)
- **Best for**: Easiest implementation, existing DLNA infrastructure
- **TV Support**: Works with any DLNA-compatible TV

## 🚀 Quick Start

### Prerequisites
- Linux system with X11 display
- Network access to target TV (192.168.200.44)
- FFmpeg installed
- Python 3.x with required packages

### Choose Your Solution

#### RTSP Streaming (Recommended for True Real-Time)
```bash
cd rtsp_streaming
bash rtsp_server_setup.sh
python3 gstreamer_rtsp_server.py
# Test: python3 rtsp_client_test.py rtsp://192.168.200.44:8554/screen
```

#### HLS Streaming (Good for Web Compatibility)
```bash
cd hls_streaming
bash hls_server_setup.sh
python3 hls_http_server.py
# Test: python3 hls_client_test.py http://192.168.200.44:8080/hls/screen.m3u8
```

#### Continuous File Streaming (Easiest Implementation)
```bash
cd continuous_file_streaming
bash continuous_stream_setup.sh
bash optimized_continuous_cast.sh
# Test: bash test_continuous_stream.sh
```

## 🛠️ Shared Tools and Utilities

All solutions include shared utilities:

- **`upnp_discovery.py`** - Network device discovery
- **`upnp_control.py`** - UPnP/DLNA control
- **`tts_enhanced.py`** - Text-to-speech system
- **`network_monitor.py`** - Network monitoring

## 📁 Directory Structure

```
├── rtsp_streaming/                 # RTSP streaming solution
│   ├── .cursor/rules/             # Cursor integration rules
│   ├── gstreamer_rtsp_server.py   # Main GStreamer server
│   ├── ffmpeg_rtsp_server.sh      # Alternative FFmpeg server
│   ├── rtsp_client_test.py        # Client testing
│   └── rtsp_server_setup.sh       # Environment setup
├── hls_streaming/                  # HLS streaming solution
│   ├── .cursor/rules/             # Cursor integration rules
│   ├── ffmpeg_hls_server.sh       # Main HLS server
│   ├── hls_http_server.py         # Python HTTP server
│   ├── hls_client_test.py         # Client testing
│   └── hls_server_setup.sh        # Environment setup
├── continuous_file_streaming/      # Continuous file streaming
│   ├── .cursor/rules/             # Cursor integration rules
│   ├── optimized_continuous_cast.sh # Main casting script
│   ├── dlna_refresh_monitor.py    # DLNA monitoring
│   ├── test_continuous_stream.sh  # Testing script
│   └── continuous_stream_setup.sh # Environment setup
├── .cursor/commands/               # Cursor commands
│   ├── mcp-*.md                   # MCP prompt commands
│   └── streaming-*.md             # Streaming-specific commands
└── test_all_streaming_solutions.sh # Master test script
```

## 🎮 Cursor Integration

### MCP Prompts
Use MCP prompts for enhanced development:

```bash
# Generate code
mcp-prompts apply_prompt mcp-code-generator --language Python --framework Flask

# Analyze performance
mcp-prompts apply_prompt mcp-analysis-prompt --analysis_type performance --target_code "streaming code"

# Generate documentation
mcp-prompts apply_prompt mcp-documentation-prompt --doc_type "API documentation" --project_name "Streaming API"

# Generate tests
mcp-prompts apply_prompt mcp-testing-prompt --test_type "unit tests" --language Python

# Debug issues
mcp-prompts apply_prompt mcp-debugging-prompt --issue_description "Streaming latency" --urgency high

# Design architecture
mcp-prompts apply_prompt mcp-architecture-prompt --system_type "streaming system" --scale medium
```

### Cursor Rules
Each solution has specific Cursor rules:
- `rtsp_streaming/.cursor/rules/rtsp-streaming.mdc`
- `hls_streaming/.cursor/rules/hls-streaming.mdc`
- `continuous_file_streaming/.cursor/rules/continuous-streaming.mdc`

## 🔧 Configuration

### Network Settings
- **Target TV**: 192.168.200.44 (Hisense TV)
- **RTSP Port**: 8554
- **HLS Port**: 8080
- **DLNA Port**: 8200

### Video Settings
- **Codec**: H.264 Baseline Profile
- **Resolution**: 1280x720
- **Frame Rate**: 30 fps
- **Pixel Format**: yuv420p

## 🧪 Testing

### Test All Solutions
```bash
bash test_all_streaming_solutions.sh
```

### Individual Testing
```bash
# RTSP
cd rtsp_streaming && python3 rtsp_client_test.py rtsp://192.168.200.44:8554/screen

# HLS
cd hls_streaming && python3 hls_client_test.py http://192.168.200.44:8080/hls/screen.m3u8

# Continuous
cd continuous_file_streaming && bash test_continuous_stream.sh
```

## 🐛 Troubleshooting

### Common Issues
1. **Permission denied**: Use `sudo` for system commands
2. **No X11 display**: Ensure you're running in a graphical environment
3. **Port conflicts**: Check if ports 8554, 8080, 8200 are available
4. **TV not connecting**: Verify network connectivity and TV support

### Debug Commands
```bash
# Check running processes
ps aux | grep -E "(rtsp|hls|continuous)"

# Check network ports
netstat -tlnp | grep -E "(8554|8080|8200)"

# Check DLNA status
sudo systemctl status minidlna

# Monitor network traffic
sudo tcpdump -i eth0 -n port 8554 or port 8080 or port 8200
```

## 📚 Documentation

Each solution includes comprehensive documentation:
- **CLAUDE.md** - Context and purpose
- **Setup scripts** - Installation and configuration
- **Test scripts** - Validation and testing
- **Monitoring tools** - Performance and status monitoring

## 🔗 Integration

### CTF Challenge Integration
- Voice alerting system integration
- Network monitoring and discovery
- Multiple streaming approaches for different scenarios
- Comprehensive testing and validation

### External Tools
- VLC Media Player for testing
- Network monitoring tools
- UPnP/DLNA discovery tools
- Text-to-speech systems

## 📈 Performance

### Latency Comparison
- **RTSP**: < 2 seconds (best)
- **HLS**: 3-10 seconds (good)
- **Continuous**: 5-15 seconds (acceptable)

### Resource Usage
- **RTSP**: High (real-time processing)
- **HLS**: Medium (segment processing)
- **Continuous**: Low (file-based)

## 🎯 Recommendations

### Choose RTSP If:
- You need true real-time streaming
- TV supports RTSP client
- Low latency is critical

### Choose HLS If:
- You need web compatibility
- TV supports HLS client
- Adaptive bitrate is needed

### Choose Continuous If:
- You want easiest implementation
- TV only supports DLNA
- Existing DLNA infrastructure

## 🤝 Contributing

1. Follow the development guidelines in each solution's `.cursor/rules/` directory
2. Use MCP prompts for code generation and analysis
3. Include comprehensive tests and documentation
4. Test with the provided validation scripts

## 📄 License

This project is part of a CTF challenge setup and follows the same licensing terms.