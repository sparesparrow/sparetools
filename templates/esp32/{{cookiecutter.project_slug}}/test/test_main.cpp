/**
 * {{cookiecutter.project_name}} - Unit Tests
 *
 * Generated from SpareTools ESP32 template
 */

#include <Arduino.h>
#include <unity.h>

// Include project headers
#include "main.cpp"

// Test setup
void setUp(void) {
    // Set up test fixtures
}

// Test teardown
void tearDown(void) {
    // Clean up after tests
}

// Basic functionality tests
void test_basic_setup(void) {
    TEST_ASSERT_TRUE(true); // Placeholder test
}

void test_wifi_initialization(void) {
{% if cookiecutter.include_wifi == 'y' %}
    // Test WiFi initialization
    TEST_ASSERT_EQUAL_STRING("{{cookiecutter.project_slug|upper}}_AP", WIFI_SSID);
{% else %}
    TEST_IGNORE_MESSAGE("WiFi not enabled in this configuration");
{% endif %}
}

{% if cookiecutter.schema_component != 'none' %}
void test_protocol_initialization(void) {
    // Test FlatBuffers initialization
    flatbuffers::FlatBufferBuilder fbb;
    TEST_ASSERT_TRUE(fbb.GetSize() == 0);
}
{% endif %}

void setup() {
    // Wait for serial to be ready
    delay(2000);

    // Start Unity test framework
    UNITY_BEGIN();

    // Run tests
    RUN_TEST(test_basic_setup);
    RUN_TEST(test_wifi_initialization);
    {% if cookiecutter.schema_component != 'none' %}
    RUN_TEST(test_protocol_initialization);
    {% endif %}

    // End tests
    UNITY_END();
}

void loop() {
    // Nothing to do in test loop
    delay(1000);
}





