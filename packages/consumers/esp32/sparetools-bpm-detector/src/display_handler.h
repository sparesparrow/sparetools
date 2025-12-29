#ifndef DISPLAY_HANDLER_H
#define DISPLAY_HANDLER_H

#include <Arduino.h>
#include "config.h"

// Display types enumeration
enum DisplayType {
    DISPLAY_NONE,
    DISPLAY_OLED_SSD1306,
    DISPLAY_7SEGMENT_TM1637
};

// Display configuration structure
struct DisplayConfig {
    DisplayType type;
    uint8_t sda_pin;
    uint8_t scl_pin;
    uint8_t clk_pin;
    uint8_t dio_pin;
    uint8_t i2c_address;
};

class DisplayHandler {
public:
    DisplayHandler();
    ~DisplayHandler();

    // Initialize display with configuration
    bool begin(DisplayType type = DISPLAY_NONE,
               uint8_t sda_pin = OLED_SDA_PIN,
               uint8_t scl_pin = OLED_SCL_PIN,
               uint8_t clk_pin = SEGMENT_CLK_PIN,
               uint8_t dio_pin = SEGMENT_DIO_PIN,
               uint8_t i2c_address = OLED_I2C_ADDRESS);

    // Legacy initialization (for backward compatibility)
    void begin();

    // Show status message
    void showStatus(const String& status);

    // Show BPM value and confidence
    void showBPM(int bpm, float confidence);

    // Clear display
    void clear();

    // Get current display type
    DisplayType getDisplayType() const { return config_.type; }

    // Check if display is initialized
    bool isInitialized() const { return initialized_; }

    // Set display brightness (for 7-segment display)
    void setBrightness(uint8_t brightness);

private:
    DisplayConfig config_;
    bool initialized_;

    // MCP-Prompts optimization: Display timing control
    unsigned long last_update_time_;     // Last display update timestamp
    unsigned long update_interval_ms_;   // Minimum interval between updates (100ms = 10 Hz)

    // OLED-specific members
#if USE_OLED_DISPLAY
    class Adafruit_SSD1306* oled_;
#endif

    // 7-segment display specific members
#if USE_7SEGMENT_DISPLAY
    class TM1637Display* seven_segment_;
#endif

    // Private initialization methods
    bool initOLED();
    bool initSevenSegment();

    // Display-specific methods
    void showStatusOLED(const String& status);
    void showStatusSevenSegment(const String& status);
    void showBPMOLED(int bpm, float confidence);
    void showBPMSevenSegment(int bpm, float confidence);
};

#endif // DISPLAY_HANDLER_H


