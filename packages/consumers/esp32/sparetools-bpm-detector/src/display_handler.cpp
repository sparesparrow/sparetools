#include "display_handler.h"

#if USE_OLED_DISPLAY
#include <Wire.h>
#include <WiFi.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#endif

#if USE_7SEGMENT_DISPLAY
#include <TM1637Display.h>
#endif

DisplayHandler::DisplayHandler()
    : initialized_(false)
#if USE_OLED_DISPLAY
    , oled_(nullptr)
#endif
#if USE_7SEGMENT_DISPLAY
    , seven_segment_(nullptr)
#endif
    , last_update_time_(0)
    , update_interval_ms_(100)  // MCP-Prompts optimized: 10 Hz refresh rate
{
    config_.type = DISPLAY_NONE;
    config_.sda_pin = OLED_SDA_PIN;
    config_.scl_pin = OLED_SCL_PIN;
    config_.clk_pin = SEGMENT_CLK_PIN;
    config_.dio_pin = SEGMENT_DIO_PIN;
    config_.i2c_address = OLED_I2C_ADDRESS;
}

DisplayHandler::~DisplayHandler() {
#if USE_OLED_DISPLAY
    if (oled_) {
        delete oled_;
        oled_ = nullptr;
    }
#endif

#if USE_7SEGMENT_DISPLAY
    if (seven_segment_) {
        delete seven_segment_;
        seven_segment_ = nullptr;
    }
#endif
}

bool DisplayHandler::begin(DisplayType type, uint8_t sda_pin, uint8_t scl_pin,
                          uint8_t clk_pin, uint8_t dio_pin, uint8_t i2c_address) {
    config_.type = type;
    config_.sda_pin = sda_pin;
    config_.scl_pin = scl_pin;
    config_.clk_pin = clk_pin;
    config_.dio_pin = dio_pin;
    config_.i2c_address = i2c_address;

    bool success = false;

    switch (type) {
        case DISPLAY_OLED_SSD1306:
#if USE_OLED_DISPLAY
            success = initOLED();
#else
            DEBUG_PRINTLN("[Display] OLED display not enabled in config.h");
#endif
            break;

        case DISPLAY_7SEGMENT_TM1637:
#if USE_7SEGMENT_DISPLAY
            success = initSevenSegment();
#else
            DEBUG_PRINTLN("[Display] 7-segment display not enabled in config.h");
#endif
            break;

        case DISPLAY_NONE:
        default:
            success = true; // Stub mode
            DEBUG_PRINTLN("[DisplayHandler] Display handler initialized (stub mode)");
            break;
    }

    initialized_ = success;

    if (!success) {
        DEBUG_PRINTLN("[Display] Failed to initialize display");
    }

    return success;
}

void DisplayHandler::begin() {
    // Legacy initialization - use config.h settings
#if USE_OLED_DISPLAY
    begin(DISPLAY_OLED_SSD1306);
#elif USE_7SEGMENT_DISPLAY
    begin(DISPLAY_7SEGMENT_TM1637);
#else
    begin(DISPLAY_NONE);
#endif
}

void DisplayHandler::showStatus(const String& status) {
    if (!initialized_) return;

    switch (config_.type) {
        case DISPLAY_OLED_SSD1306:
#if USE_OLED_DISPLAY
            showStatusOLED(status);
#endif
            break;

        case DISPLAY_7SEGMENT_TM1637:
#if USE_7SEGMENT_DISPLAY
            showStatusSevenSegment(status);
#endif
            break;

        case DISPLAY_NONE:
        default:
            // Debug output for stub mode
            #if DEBUG_SERIAL
                DEBUG_PRINTF("[Display] Status: %s\n", status.c_str());
            #endif
            break;
    }
}

void DisplayHandler::showBPM(int bpm, float confidence) {
    if (!initialized_) return;

    // MCP-Prompts optimization: Rate limit display updates to 10 Hz
    unsigned long current_time = millis();
    if (current_time - last_update_time_ < update_interval_ms_) {
        return;  // Skip update to maintain 10 Hz refresh rate
    }
    last_update_time_ = current_time;

    switch (config_.type) {
        case DISPLAY_OLED_SSD1306:
#if USE_OLED_DISPLAY
            showBPMOLED(bpm, confidence);
#endif
            break;

        case DISPLAY_7SEGMENT_TM1637:
#if USE_7SEGMENT_DISPLAY
            showBPMSevenSegment(bpm, confidence);
#endif
            break;

        case DISPLAY_NONE:
        default:
            // Debug output for stub mode
            #if DEBUG_SERIAL
                DEBUG_PRINTF("[Display] BPM: %d (Confidence: %.2f)\n", bpm, confidence);
            #endif
            break;
    }
}

void DisplayHandler::clear() {
    if (!initialized_) return;

    switch (config_.type) {
        case DISPLAY_OLED_SSD1306:
#if USE_OLED_DISPLAY
            if (oled_) {
                oled_->clearDisplay();
                oled_->display();
            }
#endif
            break;

        case DISPLAY_7SEGMENT_TM1637:
#if USE_7SEGMENT_DISPLAY
            if (seven_segment_) {
                seven_segment_->clear();
            }
#endif
            break;

        case DISPLAY_NONE:
        default:
            break;
    }
}

void DisplayHandler::setBrightness(uint8_t brightness) {
    if (!initialized_ || config_.type != DISPLAY_7SEGMENT_TM1637) return;

#if USE_7SEGMENT_DISPLAY
    if (seven_segment_) {
        seven_segment_->setBrightness(brightness);
    }
#endif
}

#if USE_OLED_DISPLAY
bool DisplayHandler::initOLED() {
    DEBUG_PRINTLN("[Display] Initializing OLED SSD1306 display");

    // Initialize I2C
    Wire.begin(config_.sda_pin, config_.scl_pin);

    // Create OLED instance
    oled_ = new Adafruit_SSD1306(128, 64, &Wire, -1); // -1 = no reset pin

    // Initialize OLED
    if (!oled_->begin(SSD1306_SWITCHCAPVCC, config_.i2c_address)) {
        DEBUG_PRINTLN("[Display] SSD1306 allocation failed");
        delete oled_;
        oled_ = nullptr;
        return false;
    }

    // Configure OLED
    oled_->clearDisplay();
    oled_->setTextSize(1);
    oled_->setTextColor(SSD1306_WHITE);
    oled_->setCursor(0, 0);

    // Display initialization message
    oled_->printf("ESP32 BPM Detector\nInitializing...");
    oled_->display();

    DEBUG_PRINTLN("[Display] OLED display initialized successfully");
    return true;
}
#endif

#if USE_7SEGMENT_DISPLAY
bool DisplayHandler::initSevenSegment() {
    DEBUG_PRINTLN("[Display] Initializing TM1637 7-segment display");

    // Create 7-segment display instance
    seven_segment_ = new TM1637Display(config_.clk_pin, config_.dio_pin);

    // Initialize display
    seven_segment_->setBrightness(0x0f); // Maximum brightness
    seven_segment_->clear();

    // Test display with "8888"
    uint8_t test_data[] = { 0xFF, 0xFF, 0xFF, 0xFF };
    seven_segment_->setSegments(test_data);

    DEBUG_PRINTLN("[Display] 7-segment display initialized successfully");
    return true;
}
#endif

#if USE_OLED_DISPLAY
void DisplayHandler::showStatusOLED(const String& status) {
    if (!oled_) return;

    oled_->clearDisplay();
    oled_->setCursor(0, 0);
    oled_->setTextSize(2);
    oled_->println("BPM Detector");
    oled_->setTextSize(1);
    oled_->println("");
    oled_->printf("Status: %s\n", status.c_str());
    oled_->printf("IP: %s\n", WiFi.localIP().toString().c_str());
    oled_->display();
}

void DisplayHandler::showBPMOLED(int bpm, float confidence) {
    if (!oled_) return;

    oled_->clearDisplay();
    oled_->setCursor(0, 0);
    oled_->setTextSize(3);
    oled_->printf("%3d\n", bpm);
    oled_->setTextSize(1);
    oled_->printf("BPM\n");
    oled_->printf("Conf: %.1f%%\n", confidence * 100.0f);
    oled_->display();
}
#endif

#if USE_7SEGMENT_DISPLAY
void DisplayHandler::showStatusSevenSegment(const String& status) {
    if (!seven_segment_) return;

    // For status messages, we'll show a pattern or just clear
    if (status == "Ready" || status == "AP Ready") {
        uint8_t data[] = { 0x00, 0x00, 0x00, 0x00 }; // Clear
        seven_segment_->setSegments(data);
    } else if (status == "Low Signal" || status == "Error") {
        uint8_t data[] = { 0x79, 0x50, 0x00, 0x00 }; // "Err"
        seven_segment_->setSegments(data);
    }
}

void DisplayHandler::showBPMSevenSegment(int bpm, float confidence) {
    if (!seven_segment_) return;

    // Display BPM value (limited to 4 digits)
    if (bpm >= 0 && bpm <= 9999) {
        seven_segment_->showNumberDec(bpm, false); // No leading zeros
    } else {
        uint8_t data[] = { 0x40, 0x40, 0x40, 0x40 }; // "----"
        seven_segment_->setSegments(data);
    }
}
#endif


