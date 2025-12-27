# Gamepad-Mapper Ecosystem API Specifications

## Overview

This document provides detailed API specifications for all components in the gamepad-mapper ecosystem. Each repository exposes well-defined APIs for integration and extension.

## gamepad-core API

### GamepadMapper Class

**Header**: `include/gamepad_mapper.h`

```cpp
class GamepadMapper {
public:
    // Construction/Destruction
    GamepadMapper();
    ~GamepadMapper();

    // Initialization
    bool initialize();
    void shutdown();

    // Configuration
    bool load_mapping(const std::string& config_path);
    bool save_mapping(const std::string& config_path);
    void clear_mapping();

    // Runtime Control
    bool start_mapping();
    void stop_mapping();
    bool is_running() const;

    // Device Management
    std::vector<GamepadDevice> get_connected_devices();
    bool add_device(const GamepadDevice& device);
    bool remove_device(int device_id);

    // Event Processing
    bool process_event(const GamepadEvent& event);
    void set_event_callback(EventCallback callback);

    // State Queries
    MappingState get_current_state() const;
    std::string get_last_error() const;

    // Advanced Features
    bool enable_macro_recording(bool enable);
    bool play_macro(const std::string& macro_name);
    bool record_macro(const std::string& macro_name);
};
```

### ControllerManager Class

**Header**: `include/controller_manager.h`

```cpp
class ControllerManager {
public:
    // Device Discovery
    bool scan_devices();
    std::vector<GamepadDeviceInfo> get_available_devices();
    bool is_device_connected(int device_id) const;

    // Device Control
    bool connect_device(int device_id);
    bool disconnect_device(int device_id);
    ControllerState get_device_state(int device_id);

    // Device Configuration
    bool set_device_deadzone(int device_id, float deadzone);
    bool calibrate_device(int device_id);
    DeviceCapabilities get_device_capabilities(int device_id);

    // Event Handling
    void set_device_callback(DeviceCallback callback);
    void set_connection_callback(ConnectionCallback callback);

    // Multi-device Support
    bool set_primary_device(int device_id);
    int get_primary_device() const;
    std::vector<int> get_connected_device_ids() const;
};
```

### Data Structures

```cpp
// Gamepad Event
struct GamepadEvent {
    int device_id;
    GamepadEventType type;
    union {
        ButtonEvent button;
        AxisEvent axis;
        HatEvent hat;
    } data;
    uint64_t timestamp;
};

// Gamepad Device
struct GamepadDevice {
    int id;
    std::string name;
    std::string vendor;
    std::string product;
    DeviceType type;
    bool is_connected;
    DeviceCapabilities capabilities;
};

// Mapping Configuration
struct MappingConfig {
    std::unordered_map<Button, InputMapping> button_mappings;
    std::unordered_map<Axis, AxisMapping> axis_mappings;
    std::unordered_map<Hat, HatMapping> hat_mappings;
    MappingOptions options;
};
```

## input-backends API

### InputSimulator Interface

**Header**: `include/backends/input_simulator.h`

```cpp
class InputSimulator {
public:
    virtual ~InputSimulator() = default;

    // Initialization
    virtual bool initialize() = 0;
    virtual void shutdown() = 0;
    virtual bool is_initialized() const = 0;

    // Keyboard Simulation
    virtual bool simulate_key_press(int key_code) = 0;
    virtual bool simulate_key_release(int key_code) = 0;
    virtual bool simulate_key_click(int key_code) = 0;

    // Mouse Simulation
    virtual bool simulate_mouse_move(int x, int y) = 0;
    virtual bool simulate_mouse_move_relative(int dx, int dy) = 0;
    virtual bool simulate_mouse_button_press(MouseButton button) = 0;
    virtual bool simulate_mouse_button_release(MouseButton button) = 0;
    virtual bool simulate_mouse_click(MouseButton button) = 0;
    virtual bool simulate_mouse_scroll(int delta_x, int delta_y) = 0;

    // Advanced Features
    virtual bool simulate_text_input(const std::string& text) = 0;
    virtual bool get_cursor_position(int& x, int& y) = 0;
    virtual bool set_cursor_position(int x, int y) = 0;

    // Backend Information
    virtual std::string get_backend_name() const = 0;
    virtual BackendCapabilities get_capabilities() const = 0;
    virtual bool is_available() const = 0;
};
```

### Backend Factory Functions

```cpp
// Factory functions for creating simulators
std::unique_ptr<InputSimulator> create_x11_simulator();
std::unique_ptr<InputSimulator> create_wayland_simulator();
std::unique_ptr<InputSimulator> create_kde_simulator();
std::unique_ptr<InputSimulator> create_sdl2_simulator();
std::unique_ptr<InputSimulator> create_uinput_simulator();

// Backend manager for automatic selection
class InputBackendManager {
public:
    bool initialize();
    std::unique_ptr<InputSimulator> create_best_simulator();
    std::vector<std::string> get_available_backends();
    bool set_preferred_backend(const std::string& backend_name);
};
```

## gamepad-mcp-server API

### MCP Server Interface

**Header**: `include/mcp_server.h`

```cpp
class MCPServer {
public:
    // Server Lifecycle
    bool initialize(const ServerConfig& config);
    bool start();
    void stop();
    bool is_running() const;

    // Tool Registration
    bool register_tool(const std::string& name,
                      const std::string& description,
                      ToolHandler handler);
    bool unregister_tool(const std::string& name);

    // Resource Management
    bool register_resource(const std::string& uri,
                          const std::string& name,
                          const std::string& description,
                          const std::string& mime_type);
    bool update_resource(const std::string& uri, const std::string& content);

    // Prompt Management
    bool register_prompt(const std::string& name,
                        const std::string& description,
                        PromptHandler handler);

    // Server Information
    ServerInfo get_server_info() const;
    std::vector<ToolInfo> get_registered_tools() const;
    std::vector<ResourceInfo> get_registered_resources() const;
};
```

### Gamepad MCP Integration

**Header**: `include/gamepad_server.h`

```cpp
class GamepadServer : public MCPServer {
public:
    // Gamepad Control Tools
    bool register_gamepad_tools();
    bool register_device_tools();
    bool register_mapping_tools();
    bool register_audio_tools();

    // Device Management
    std::vector<GamepadDevice> get_connected_devices();
    bool load_device_mapping(int device_id, const std::string& mapping_name);

    // Mapping Operations
    bool create_mapping(const std::string& name, const MappingConfig& config);
    bool update_mapping(const std::string& name, const MappingConfig& config);
    bool delete_mapping(const std::string& name);

    // Audio Integration
    bool enable_voice_alerts(bool enable);
    bool play_sound_effect(const std::string& effect_name);

    // Bluetooth Integration
    bool scan_bluetooth_devices();
    bool connect_bluetooth_device(const std::string& device_address);
};
```

### MCP Tool Specifications

#### Device Management Tools

```json
{
  "name": "gamepad_list_devices",
  "description": "List all connected gamepad devices with their capabilities",
  "inputSchema": {
    "type": "object",
    "properties": {
      "include_bluetooth": {
        "type": "boolean",
        "description": "Include Bluetooth devices in the list",
        "default": true
      }
    }
  }
}

{
  "name": "gamepad_connect_device",
  "description": "Connect to a specific gamepad device",
  "inputSchema": {
    "type": "object",
    "properties": {
      "device_id": {
        "type": "integer",
        "description": "Device ID to connect"
      },
      "device_address": {
        "type": "string",
        "description": "Bluetooth device address (optional)"
      }
    },
    "required": ["device_id"]
  }
}
```

#### Mapping Management Tools

```json
{
  "name": "gamepad_load_mapping",
  "description": "Load a gamepad mapping configuration",
  "inputSchema": {
    "type": "object",
    "properties": {
      "mapping_name": {
        "type": "string",
        "description": "Name of the mapping preset to load"
      },
      "device_id": {
        "type": "integer",
        "description": "Device ID to apply mapping to (optional)"
      }
    },
    "required": ["mapping_name"]
  }
}

{
  "name": "gamepad_remap_button",
  "description": "Remap a gamepad button to keyboard/mouse input",
  "inputSchema": {
    "type": "object",
    "properties": {
      "button": {
        "type": "string",
        "enum": ["A", "B", "X", "Y", "LB", "RB", "LT", "RT", "START", "SELECT", "LS", "RS"]
      },
      "input_type": {
        "type": "string",
        "enum": ["keyboard", "mouse_button", "mouse_scroll", "none"]
      },
      "key_code": {
        "type": "integer",
        "description": "Key code for keyboard input"
      },
      "mouse_button": {
        "type": "string",
        "enum": ["left", "right", "middle"]
      }
    },
    "required": ["button", "input_type"]
  }
}
```

## gamepad-bluetooth API

### BluetoothScanner Class

**Header**: `include/bluetooth_scanner.h`

```cpp
class BluetoothScanner {
public:
    // Scanner Control
    bool initialize();
    bool start_scan(int timeout_seconds = 10);
    void stop_scan();
    bool is_scanning() const;

    // Device Discovery
    std::vector<BluetoothDevice> get_discovered_devices();
    std::vector<BluetoothDevice> get_paired_devices();
    bool is_device_available(const std::string& address);

    // Device Information
    BluetoothDeviceInfo get_device_info(const std::string& address);
    DeviceCapabilities get_device_capabilities(const std::string& address);

    // Callbacks
    void set_device_found_callback(DeviceFoundCallback callback);
    void set_scan_complete_callback(ScanCompleteCallback callback);

    // Filtering
    void set_device_filter(const DeviceFilter& filter);
    void clear_device_filter();
};
```

### BluetoothConnector Class

**Header**: `include/bluetooth_connector.h`

```cpp
class BluetoothConnector {
public:
    // Connection Management
    bool connect(const BluetoothDevice& device);
    bool disconnect();
    bool reconnect();
    ConnectionStatus get_connection_status() const;

    // Device Communication
    bool send_command(const std::vector<uint8_t>& command);
    std::vector<uint8_t> receive_data(size_t max_size = 1024);
    bool is_data_available();

    // Device Control
    bool pair_device(const BluetoothDevice& device);
    bool unpair_device(const std::string& address);
    bool trust_device(const std::string& address);

    // HID Protocol
    HIDDeviceInfo get_hid_info();
    bool set_hid_report_mode(HIDReportMode mode);
    std::vector<HIDReport> get_pending_reports();

    // Callbacks
    void set_connection_callback(ConnectionCallback callback);
    void set_data_received_callback(DataReceivedCallback callback);
    void set_disconnection_callback(DisconnectionCallback callback);
};
```

### HIDParser Class

**Header**: `include/hid_parser.h`

```cpp
class HIDParser {
public:
    // Report Parsing
    bool parse_report(const std::vector<uint8_t>& report_data,
                     GamepadEvent& event);
    bool validate_report(const std::vector<uint8_t>& report_data);

    // Device Descriptor
    bool parse_descriptor(const std::vector<uint8_t>& descriptor);
    HIDDeviceInfo get_device_info() const;
    std::vector<HIDUsage> get_supported_usages() const;

    // Report Descriptor
    ReportDescriptor get_report_descriptor() const;
    std::vector<ReportField> get_report_fields() const;

    // Calibration
    bool calibrate_axis(AxisType axis, const CalibrationData& data);
    CalibrationData get_axis_calibration(AxisType axis) const;

    // Error Handling
    std::string get_last_parse_error() const;
    bool has_parse_error() const;
    void clear_parse_error();
};
```

## gamepad-audio API

### AudioBackend Interface

**Header**: `include/audio_backend.h`

```cpp
class AudioBackend {
public:
    virtual ~AudioBackend() = default;

    // Initialization
    virtual bool initialize() = 0;
    virtual void shutdown() = 0;
    virtual bool is_initialized() const = 0;

    // Playback Control
    virtual bool play_sound(const std::string& sound_file) = 0;
    virtual bool play_sound_buffer(const std::vector<uint8_t>& audio_data,
                                  AudioFormat format) = 0;
    virtual bool stop_playback() = 0;
    virtual PlaybackStatus get_playback_status() const = 0;

    // Volume Control
    virtual bool set_volume(float volume) = 0;
    virtual float get_volume() const = 0;
    virtual bool mute(bool mute) = 0;
    virtual bool is_muted() const = 0;

    // Device Management
    virtual std::vector<AudioDevice> get_available_devices() = 0;
    virtual bool set_output_device(const std::string& device_id) = 0;
    virtual AudioDevice get_current_device() const = 0;

    // Audio Information
    virtual AudioCapabilities get_capabilities() const = 0;
    virtual std::string get_backend_name() const = 0;
};
```

### VoiceAlerts Class

**Header**: `include/voice_alerts.h`

```cpp
class VoiceAlerts {
public:
    // Initialization
    bool initialize();
    void shutdown();
    bool is_initialized() const;

    // Voice Synthesis
    bool speak_text(const std::string& text);
    bool speak_text_async(const std::string& text);
    bool stop_speaking();
    bool is_speaking() const;

    // Alert Management
    bool register_alert(GamepadEventType event_type,
                       const std::string& alert_text);
    bool unregister_alert(GamepadEventType event_type);
    std::vector<GamepadEventType> get_registered_alerts() const;

    // Voice Configuration
    bool set_voice(const std::string& voice_name);
    bool set_voice_parameters(int pitch, int speed, int volume);
    VoiceParameters get_voice_parameters() const;
    std::vector<std::string> get_available_voices() const;

    // Sound Effects
    bool play_sound_effect(const std::string& effect_name);
    bool register_sound_effect(const std::string& name,
                              const std::string& sound_file);
    bool unregister_sound_effect(const std::string& name);

    // Queue Management
    size_t get_queue_size() const;
    bool clear_queue();
    bool set_queue_limit(size_t limit);
};
```

## gamepad-config API

### ConfigManager Class

**Header**: `include/config_manager.h`

```cpp
class ConfigManager {
public:
    // Configuration Loading
    bool load_config(const std::string& config_path);
    bool load_config_from_string(const std::string& config_json);
    bool save_config(const std::string& config_path);
    void clear_config();

    // Configuration Access
    nlohmann::json get_config() const;
    bool set_config(const nlohmann::json& config);
    bool update_config(const std::string& key_path, const nlohmann::json& value);
    nlohmann::json get_value(const std::string& key_path) const;

    // Validation
    bool validate_config() const;
    bool validate_config(const nlohmann::json& config) const;
    std::vector<ValidationError> get_validation_errors() const;

    // Schema Management
    bool set_schema(const nlohmann::json& schema);
    nlohmann::json get_schema() const;
    bool validate_against_schema(const nlohmann::json& config) const;

    // Configuration Sections
    bool has_section(const std::string& section_name) const;
    nlohmann::json get_section(const std::string& section_name) const;
    bool set_section(const std::string& section_name, const nlohmann::json& section);

    // File Operations
    bool import_config(const std::string& import_path);
    bool export_config(const std::string& export_path, ConfigFormat format);
    bool merge_config(const nlohmann::json& other_config);
};
```

### PresetManager Class

**Header**: `include/preset_manager.h`

```cpp
class PresetManager {
public:
    // Preset Directory Management
    bool load_preset_directory(const std::string& directory_path);
    bool add_preset_directory(const std::string& directory_path);
    void clear_preset_directories();
    std::vector<std::string> get_preset_directories() const;

    // Preset Discovery
    std::vector<PresetInfo> get_available_presets() const;
    std::vector<PresetInfo> get_presets_by_category(const std::string& category) const;
    bool preset_exists(const std::string& preset_name) const;

    // Preset Loading
    nlohmann::json load_preset(const std::string& preset_name);
    bool load_preset_to_config(const std::string& preset_name, ConfigManager& config);
    PresetMetadata get_preset_metadata(const std::string& preset_name) const;

    // Preset Management
    bool save_preset(const std::string& preset_name, const nlohmann::json& config);
    bool save_preset(const std::string& preset_name, const nlohmann::json& config,
                    const PresetMetadata& metadata);
    bool delete_preset(const std::string& preset_name);
    bool rename_preset(const std::string& old_name, const std::string& new_name);

    // Preset Categories
    std::vector<std::string> get_categories() const;
    bool set_preset_category(const std::string& preset_name, const std::string& category);
    std::string get_preset_category(const std::string& preset_name) const;

    // Preset Validation
    bool validate_preset(const std::string& preset_name) const;
    bool validate_preset(const nlohmann::json& preset_config) const;
    std::vector<ValidationError> get_preset_validation_errors(const std::string& preset_name) const;
};
```

## Error Handling

All APIs follow consistent error handling patterns:

```cpp
// Error codes
enum class GamepadError {
    SUCCESS = 0,
    INITIALIZATION_FAILED,
    DEVICE_NOT_FOUND,
    CONNECTION_LOST,
    INVALID_CONFIGURATION,
    BACKEND_NOT_AVAILABLE,
    PERMISSION_DENIED,
    TIMEOUT,
    INVALID_PARAMETER,
    OUT_OF_MEMORY,
    UNKNOWN_ERROR
};

// Error information
struct ErrorInfo {
    GamepadError code;
    std::string message;
    std::string details;
    std::source_location location;
};

// Error handling in methods
std::expected<T, ErrorInfo> method_name(Parameters...);
```

## Thread Safety

### Thread Safety Guarantees

- **gamepad-core**: Thread-safe for concurrent event processing
- **input-backends**: Backend-specific (X11: thread-safe, Wayland: single-threaded)
- **gamepad-mcp-server**: Thread-safe for concurrent MCP requests
- **gamepad-bluetooth**: Thread-safe for connection management
- **gamepad-audio**: Thread-safe for playback operations
- **gamepad-config**: Thread-safe for configuration access

### Synchronization Primitives

```cpp
// Mutex-protected operations
std::mutex& get_mutex();

// Atomic operations for state
std::atomic<bool> is_initialized_;
std::atomic<ConnectionStatus> connection_status_;
```

## Memory Management

### RAII Principles

All classes follow RAII (Resource Acquisition Is Initialization) principles:

```cpp
class GamepadMapper {
public:
    GamepadMapper();  // Acquire resources
    ~GamepadMapper(); // Release resources
    // No copy/move operations (non-copyable)
    GamepadMapper(const GamepadMapper&) = delete;
    GamepadMapper& operator=(const GamepadMapper&) = delete;
};
```

### Smart Pointer Usage

```cpp
// Factory functions return unique_ptr
std::unique_ptr<InputSimulator> create_x11_simulator();

// Internal management uses shared_ptr for reference counting
std::shared_ptr<DeviceManager> device_manager_;
```

## Version Compatibility

### Semantic Versioning

All APIs follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### API Version Macros

```cpp
#define GAMEPAD_CORE_API_VERSION "1.0.0"
#define INPUT_BACKENDS_API_VERSION "1.0.0"
#define MCP_SERVER_API_VERSION "1.0.0"
#define BLUETOOTH_API_VERSION "1.0.0"
#define AUDIO_API_VERSION "1.0.0"
#define CONFIG_API_VERSION "1.0.0"
```

This API specification provides the foundation for developing against and extending the gamepad-mapper ecosystem. Each component is designed to be independently useful while integrating seamlessly with the broader system.