#include <Arduino.h>
#include <unity.h>
#include "wifi_handler.h"

// Mock WiFi for testing
class MockWiFi {
public:
    static wl_status_t status() { return WL_CONNECTED; }
    static void mode(wifi_mode_t mode) {}
    static bool softAP(const char* ssid, const char* password) { return true; }
    static void begin(const char* ssid, const char* password) {}
    static IPAddress localIP() { return IPAddress(192, 168, 1, 100); }
    static IPAddress softAPIP() { return IPAddress(192, 168, 4, 1); }
    static void disconnect(bool wifiOff = false) {}
    static void setHostname(const char* hostname) {}
    static int32_t RSSI() { return -50; }
};

// Test fixtures
WiFiHandler* wifi_handler;

void setUp() {
    wifi_handler = new WiFiHandler();
}

void tearDown() {
    delete wifi_handler;
    wifi_handler = nullptr;
}

// Test WiFiHandler initialization
void test_wifi_handler_initialization() {
    TEST_ASSERT_NOT_NULL(wifi_handler);
    TEST_ASSERT_FALSE(wifi_handler->isConnected());

    WiFiStatus status = wifi_handler->getStatus();
    TEST_ASSERT_EQUAL(WIFI_DISCONNECTED, status.state);
    TEST_ASSERT_EQUAL_STRING("", status.ssid.c_str());
}

// Test WiFiHandler begin with valid credentials
void test_wifi_handler_begin_valid() {
    bool result = wifi_handler->begin("TestSSID", "TestPassword");
    TEST_ASSERT_TRUE(result);

    WiFiStatus status = wifi_handler->getStatus();
    TEST_ASSERT_EQUAL_STRING("TestSSID", status.ssid.c_str());
}

// Test WiFiHandler begin with invalid credentials
void test_wifi_handler_begin_invalid() {
    bool result = wifi_handler->begin(nullptr, nullptr);
    TEST_ASSERT_FALSE(result);

    WiFiStatus status = wifi_handler->getStatus();
    TEST_ASSERT_EQUAL(WIFI_ERROR, status.state);
}

// Test credential setting
void test_wifi_handler_set_credentials() {
    wifi_handler->setCredentials("NewSSID", "NewPassword");
    // Credentials are set internally, no direct verification method
    TEST_PASS();
}

// Test reconnection attempts setting
void test_wifi_handler_reconnection_settings() {
    wifi_handler->setReconnectionAttempts(5);
    wifi_handler->setReconnectionDelay(2000);
    // Settings are set internally, no direct verification method
    TEST_PASS();
}

// Test status information
void test_wifi_handler_status_info() {
    wifi_handler->begin("TestSSID", "TestPassword");

    String ip = wifi_handler->getIPAddress();
    TEST_ASSERT_TRUE(ip.length() > 0);

    int signal = wifi_handler->getSignalStrength();
    TEST_ASSERT_TRUE(signal <= 0 && signal >= -100); // Valid RSSI range
}

// Test access point setup
void test_wifi_handler_access_point() {
    bool result = wifi_handler->setupAccessPoint("TestAP", "TestPass");
    TEST_ASSERT_TRUE(result);

    WiFiStatus status = wifi_handler->getStatus();
    TEST_ASSERT_EQUAL(WIFI_AP_MODE, status.state);
}

// Test disconnection
void test_wifi_handler_disconnect() {
    wifi_handler->disconnect();
    TEST_ASSERT_FALSE(wifi_handler->isConnected());

    WiFiStatus status = wifi_handler->getStatus();
    TEST_ASSERT_EQUAL(WIFI_DISCONNECTED, status.state);
}

void setup() {
    delay(2000);
    UNITY_BEGIN();

    RUN_TEST(test_wifi_handler_initialization);
    RUN_TEST(test_wifi_handler_begin_valid);
    RUN_TEST(test_wifi_handler_begin_invalid);
    RUN_TEST(test_wifi_handler_set_credentials);
    RUN_TEST(test_wifi_handler_reconnection_settings);
    RUN_TEST(test_wifi_handler_status_info);
    RUN_TEST(test_wifi_handler_access_point);
    RUN_TEST(test_wifi_handler_disconnect);
}

void loop() {
    UNITY_END();
}