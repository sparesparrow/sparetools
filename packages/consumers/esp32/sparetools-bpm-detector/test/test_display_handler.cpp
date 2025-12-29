#include <Arduino.h>
#include <unity.h>
#include "display_handler.h"

// Mock display classes for testing
class MockAdafruit_SSD1306 {
public:
    MockAdafruit_SSD1306(uint8_t w, uint8_t h, void* wire, int reset) : width(w), height(h) {}
    bool begin(uint8_t switchvcc, uint16_t addr) { return initialized = true; }
    void clearDisplay() {}
    void setTextSize(uint8_t s) { textSize = s; }
    void setTextColor(uint16_t c) { textColor = c; }
    void setCursor(int16_t x, int16_t y) { cursorX = x; cursorY = y; }
    void printf(const char* format, ...) {}
    void display() {}
    bool initialized = false;
    uint8_t width, height, textSize;
    uint16_t textColor;
    int16_t cursorX, cursorY;
};

class MockTM1637Display {
public:
    MockTM1637Display(uint8_t clk, uint8_t dio) : clkPin(clk), dioPin(dio) {}
    void setBrightness(uint8_t brightness) { this->brightness = brightness; }
    void clear() { segments = 0; }
    void showNumberDec(int num, bool leading_zero) { segments = num; }
    void setSegments(const uint8_t segments[], uint8_t length = 4, uint8_t pos = 0) {
        memcpy(this->segments_array, segments, min(length, (uint8_t)4));
    }
    uint8_t clkPin, dioPin, brightness;
    int segments;
    uint8_t segments_array[4];
};

// Test fixtures
DisplayHandler* display_handler;

void setUp() {
    display_handler = new DisplayHandler();
}

void tearDown() {
    delete display_handler;
    display_handler = nullptr;
}

// Test DisplayHandler initialization with no display
void test_display_handler_init_none() {
    bool result = display_handler->begin(DISPLAY_NONE);
    TEST_ASSERT_TRUE(result);
    TEST_ASSERT_TRUE(display_handler->isInitialized());
    TEST_ASSERT_EQUAL(DISPLAY_NONE, display_handler->getDisplayType());
}

// Test DisplayHandler status messages with no display
void test_display_handler_status_none() {
    display_handler->begin(DISPLAY_NONE);
    display_handler->showStatus("Test Status");
    // Should not crash, just debug output
    TEST_PASS();
}

// Test DisplayHandler BPM display with no display
void test_display_handler_bpm_none() {
    display_handler->begin(DISPLAY_NONE);
    display_handler->showBPM(128, 0.85f);
    // Should not crash, just debug output
    TEST_PASS();
}

// Test DisplayHandler clear with no display
void test_display_handler_clear_none() {
    display_handler->begin(DISPLAY_NONE);
    display_handler->clear();
    TEST_PASS();
}

// Test invalid display type handling
void test_display_handler_invalid_type() {
    bool result = display_handler->begin((DisplayType)999);
    TEST_ASSERT_FALSE(result);
    TEST_ASSERT_FALSE(display_handler->isInitialized());
}

// Test display type enumeration values
void test_display_type_enum() {
    TEST_ASSERT_EQUAL(0, DISPLAY_NONE);
    TEST_ASSERT_EQUAL(1, DISPLAY_OLED_SSD1306);
    TEST_ASSERT_EQUAL(2, DISPLAY_7SEGMENT_TM1637);
}

// Test configuration structure
void test_display_config() {
    DisplayConfig config;
    config.type = DISPLAY_OLED_SSD1306;
    config.sda_pin = 21;
    config.scl_pin = 22;
    config.i2c_address = 0x3C;

    TEST_ASSERT_EQUAL(DISPLAY_OLED_SSD1306, config.type);
    TEST_ASSERT_EQUAL(21, config.sda_pin);
    TEST_ASSERT_EQUAL(22, config.scl_pin);
    TEST_ASSERT_EQUAL(0x3C, config.i2c_address);
}

void setup() {
    delay(2000);
    UNITY_BEGIN();

    RUN_TEST(test_display_handler_init_none);
    RUN_TEST(test_display_handler_status_none);
    RUN_TEST(test_display_handler_bpm_none);
    RUN_TEST(test_display_handler_clear_none);
    RUN_TEST(test_display_handler_invalid_type);
    RUN_TEST(test_display_type_enum);
    RUN_TEST(test_display_config);
}

void loop() {
    UNITY_END();
}