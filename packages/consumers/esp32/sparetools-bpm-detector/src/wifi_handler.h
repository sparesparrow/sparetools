#ifndef WIFI_HANDLER_H
#define WIFI_HANDLER_H

#include <WiFi.h>
#include <WiFiClient.h>
#include <ESPmDNS.h>
#include <ArduinoOTA.h>
#include "config.h"

// WiFi connection states
enum WiFiState {
    WIFI_DISCONNECTED,
    WIFI_CONNECTING,
    WIFI_CONNECTED,
    WIFI_AP_MODE,
    WIFI_ERROR
};

// WiFi connection result
struct WiFiStatus {
    WiFiState state;
    String ssid;
    String ipAddress;
    int signalStrength;
    String errorMessage;
    unsigned long lastConnectionAttempt;
    unsigned long connectionDuration;
};

class WiFiHandler {
public:
    WiFiHandler();
    ~WiFiHandler();

    // Core WiFi management methods
    bool begin(const char* ssid, const char* password);
    bool connect();
    void disconnect();
    bool reconnect();
    bool isConnected();

    // Status and information methods
    WiFiStatus getStatus();
    String getIPAddress();
    int getSignalStrength();

    // Access Point fallback
    bool setupAccessPoint(const char* ap_ssid = nullptr, const char* ap_password = nullptr);

    // Runtime configuration
    void setCredentials(const char* ssid, const char* password);
    void setReconnectionAttempts(int max_attempts);
    void setReconnectionDelay(unsigned long initial_delay_ms);

    // Monitoring and maintenance
    void update();  // Call this regularly in loop()
    void resetConnectionAttempts();

    // Optional features (enabled via config.h)
#if ENABLE_MDNS
    bool setupMDNS(const char* hostname = MDNS_HOSTNAME);
#endif

#if ENABLE_OTA
    bool setupOTA(const char* password = OTA_PASSWORD);
#endif

    // Web server setup (called automatically on WiFi connect)
    void setupWebServer();

private:
    // Connection management
    String _ssid;
    String _password;
    String _ap_ssid;
    String _ap_password;
    WiFiState _currentState;
    String _errorMessage;

    // Reconnection logic
    int _maxReconnectionAttempts;
    int _currentReconnectionAttempt;
    unsigned long _reconnectionDelay;
    unsigned long _lastReconnectionAttempt;
    unsigned long _connectionStartTime;

    // Signal strength tracking
    int _lastSignalStrength;

    // Private helper methods
    bool _attemptConnection();
    void _updateState();
    void _handleReconnection();
    bool _validateCredentials();
    String _getWiFiErrorString(wl_status_t status);

    // Exponential backoff calculation
    unsigned long _calculateBackoffDelay();

    // Optional feature flags
    bool _mdnsEnabled;
    bool _otaEnabled;
};

#endif // WIFI_HANDLER_H