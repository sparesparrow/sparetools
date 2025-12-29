#ifndef CONFIG_H
#define CONFIG_H

// ============================================================================
// WiFi Configuration
// ============================================================================
#define WIFI_SSID "Prospects"
#define WIFI_PASSWORD "Romy1337"

// ============================================================================
// Hardware Configuration
// ============================================================================
// Microphone input pin (ADC pin on ESP32-S3)
// ESP32-S3 ADC1 pins: GPIO1, GPIO2, GPIO3, GPIO4, GPIO5, GPIO6, GPIO7, GPIO8, GPIO9, GPIO10
#define MICROPHONE_PIN 1            // GPIO1 (ADC1_CH0 on ESP32-S3)

// Display configuration
#define USE_OLED_DISPLAY 0          // Set to 1 to enable SSD1306 OLED
#define USE_7SEGMENT_DISPLAY 0      // Set to 1 to enable TM1637 7-segment display
#define OLED_SDA_PIN 21             // I2C SDA for OLED
#define OLED_SCL_PIN 22             // I2C SCL for OLED
#define OLED_I2C_ADDRESS 0x3C       // Default I2C address for SSD1306
#define SEGMENT_CLK_PIN 18          // CLK for TM1637
#define SEGMENT_DIO_PIN 19          // DIO for TM1637

// ============================================================================
// Audio Configuration - MCP-Prompts Optimized
// ============================================================================
// MCP-Prompts /esp32-bpm-fft-configuration recommendations:
// - sample_rate: 25000 Hz (validated for ESP32-S3 performance)
// - fft_size: 1024 (good balance of frequency resolution vs computation time)
// - window_type: hamming (recommended for BPM detection)
// ESP32-S3 constraints: 240MHz CPU, 512KB RAM, FPU available
#define SAMPLE_RATE 25000           // Sampling rate in Hz (25 kHz is good balance)
#define FFT_SIZE 1024               // FFT size (power of 2: 256, 512, 1024)
#define ADC_RESOLUTION 12           // ESP32 ADC resolution (12 bits max)

// FFT Window Configuration (MCP-Prompts optimized)
#define FFT_WINDOW_TYPE "HAMMING"   // Hamming window for BPM detection
#define FFT_OVERLAP_RATIO 0.5f      // 50% overlap for better temporal resolution

// ============================================================================
// BPM Detection Configuration
// ============================================================================
#define MIN_BPM 60                  // Minimum BPM to detect
#define MAX_BPM 200                 // Maximum BPM to detect
#define DETECTION_THRESHOLD 0.5     // Threshold for beat detection (0.0-1.0)
#define CONFIDENCE_THRESHOLD 0.3    // Minimum confidence to report BPM (0.0-1.0)

// FFT frequency range for bass detection
// BPM is typically found in bass frequencies (40-100 Hz for kick drum)
#define BASS_FREQ_MIN 40            // Minimum frequency for bass (Hz)
#define BASS_FREQ_MAX 200           // Maximum frequency for bass (Hz)

// ============================================================================
// Envelope Detection Configuration
// ============================================================================
#define ENVELOPE_DECAY 0.9          // Envelope decay factor (0.8-0.99)
#define ENVELOPE_RELEASE 0.95       // Envelope release factor (0.9-0.99)
#define MIN_BEAT_INTERVAL 300       // Minimum milliseconds between beats (60-200 BPM)
#define MAX_BEAT_INTERVAL 1000      // Maximum milliseconds between beats

// ============================================================================
// Buffer & Memory Configuration
// ============================================================================
#define BEAT_HISTORY_SIZE 32        // Number of recent beats to track for BPM calculation
#define SAMPLES_PER_DETECTION 512   // Number of samples per detection cycle

// ============================================================================
// WiFi Server Configuration
// ============================================================================
#define SERVER_PORT 80              // HTTP server port
#define API_POLL_INTERVAL 100       // API update interval in milliseconds

// ============================================================================
// Logging & Debug Configuration
// ============================================================================
#define DEBUG_SERIAL 1              // Enable serial debugging output
#define DEBUG_FFT 0                 // Enable FFT debug output (verbose)
#define DEBUG_BEATS 0               // Enable beat detection debug
#define DEBUG_MEMORY 1              // Enable memory usage logging

#if DEBUG_SERIAL
    #define DEBUG_PRINT(x) Serial.print(x)
    #define DEBUG_PRINTLN(x) Serial.println(x)
    #define DEBUG_PRINTF(fmt, ...) Serial.printf(fmt, ##__VA_ARGS__)
    #define DEBUG_FLUSH() Serial.flush()
#else
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINTLN(x)
    #define DEBUG_PRINTF(fmt, ...)
    #define DEBUG_FLUSH()
#endif

// ============================================================================
// Optional Features
// ============================================================================
#define ENABLE_MQTT 0               // Enable MQTT publishing (requires WiFi)
#define MQTT_BROKER "mqtt.example.com"
#define MQTT_PORT 1883
#define MQTT_TOPIC "home/bpm"

#define ENABLE_MDNS 1               // Enable mDNS for .local domain (e.g., esp32-bpm.local)
#define MDNS_HOSTNAME "esp32-bpm"

#define ENABLE_OTA 1                // Enable Over-The-Air updates
#define OTA_PASSWORD "admin123"

// ============================================================================
// Performance Tuning
// ============================================================================
#define TASK_PRIORITY 2             // FreeRTOS task priority for audio sampling
#define TASK_STACK_SIZE 4096        // Task stack size in bytes
#define TASK_CORE 0                 // Core to run audio task (0 or 1)

// ADC attenuation: controls max voltage measurement
// ADC_ATTEN_DB_0  : 0 dB attenuation, max 1.0V
// ADC_ATTEN_DB_2_5: 2.5 dB attenuation, max 1.5V
// ADC_ATTEN_DB_6  : 6 dB attenuation, max 2.0V
// ADC_ATTEN_DB_11 : 11 dB attenuation, max 3.6V (recommended for MAX9814)
#define ADC_ATTENUATION ADC_ATTEN_DB_11

// ============================================================================
// Validation Checks
// ============================================================================
#if FFT_SIZE & (FFT_SIZE - 1)
    #error "FFT_SIZE must be a power of 2 (256, 512, 1024, 2048, etc.)"
#endif

#if SAMPLE_RATE < 8000 || SAMPLE_RATE > 48000
    #warning "SAMPLE_RATE should be between 8000 and 48000 Hz for optimal results"
#endif

#if MIN_BPM < 30 || MAX_BPM > 300
    #warning "BPM range (30-300) seems unusual"
#endif

#endif // CONFIG_H
