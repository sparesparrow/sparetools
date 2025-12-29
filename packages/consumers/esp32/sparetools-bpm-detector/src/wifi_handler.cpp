#include "wifi_handler.h"
#include "config.h"
#include <Arduino.h>
#include <WebServer.h>
#include "api_endpoints.h"

// Global web server instance (shared with main.cpp)
extern WebServer* server;

WiFiHandler::WiFiHandler()
    : _currentState(WIFI_DISCONNECTED)
    , _maxReconnectionAttempts(10)
    , _currentReconnectionAttempt(0)
    , _reconnectionDelay(1000)  // Start with 1 second
    , _lastReconnectionAttempt(0)
    , _connectionStartTime(0)
    , _lastSignalStrength(-100)
    , _mdnsEnabled(false)
    , _otaEnabled(false)
{
}

WiFiHandler::~WiFiHandler() {
    disconnect();
}

bool WiFiHandler::begin(const char* ssid, const char* password) {
    if (!ssid || !password) {
        _errorMessage = "Invalid SSID or password";
        _currentState = WIFI_ERROR;
        return false;
    }

    _ssid = ssid;
    _password = password;
    _ap_ssid = String(ssid) + "_AP";
    _ap_password = password;

    DEBUG_PRINTLN("[WiFi] Initializing WiFi handler");

    // Set hostname for better network identification
    WiFi.setHostname(String(MDNS_HOSTNAME).c_str());

    _currentState = WIFI_DISCONNECTED;
    _errorMessage = "";

    return true;
}

bool WiFiHandler::connect() {
    if (_ssid.isEmpty() || _password.isEmpty()) {
        _errorMessage = "No credentials set";
        _currentState = WIFI_ERROR;
        return false;
    }

    DEBUG_PRINTLN("[WiFi] Attempting connection to: " + _ssid);

    _currentState = WIFI_CONNECTING;
    _lastReconnectionAttempt = millis();

    return _attemptConnection();
}

void WiFiHandler::disconnect() {
    DEBUG_PRINTLN("[WiFi] Disconnecting from WiFi");

    WiFi.disconnect(true);
    _currentState = WIFI_DISCONNECTED;
    _connectionStartTime = 0;
    _currentReconnectionAttempt = 0;
    _errorMessage = "";
}

bool WiFiHandler::reconnect() {
    if (_currentState == WIFI_CONNECTED) {
        return true;  // Already connected
    }

    if (_currentReconnectionAttempt >= _maxReconnectionAttempts) {
        DEBUG_PRINTLN("[WiFi] Max reconnection attempts reached, falling back to AP mode");
        return setupAccessPoint();
    }

    unsigned long now = millis();
    unsigned long timeSinceLastAttempt = now - _lastReconnectionAttempt;

    if (timeSinceLastAttempt < _calculateBackoffDelay()) {
        return false;  // Wait for backoff delay
    }

    _currentReconnectionAttempt++;
    _lastReconnectionAttempt = now;

    DEBUG_PRINTF("[WiFi] Reconnection attempt %d/%d\n", _currentReconnectionAttempt, _maxReconnectionAttempts);

    return _attemptConnection();
}

bool WiFiHandler::isConnected() {
    return (WiFi.status() == WL_CONNECTED) && (_currentState == WIFI_CONNECTED);
}

WiFiStatus WiFiHandler::getStatus() {
    WiFiStatus status;
    status.state = _currentState;
    status.ssid = _ssid;
    status.ipAddress = getIPAddress();
    status.signalStrength = getSignalStrength();
    status.errorMessage = _errorMessage;
    status.lastConnectionAttempt = _lastReconnectionAttempt;

    if (_connectionStartTime > 0) {
        status.connectionDuration = millis() - _connectionStartTime;
    } else {
        status.connectionDuration = 0;
    }

    return status;
}

String WiFiHandler::getIPAddress() {
    if (WiFi.getMode() == WIFI_AP) {
        return WiFi.softAPIP().toString();
    } else if (WiFi.status() == WL_CONNECTED) {
        return WiFi.localIP().toString();
    }
    return "0.0.0.0";
}

int WiFiHandler::getSignalStrength() {
    if (WiFi.status() == WL_CONNECTED) {
        _lastSignalStrength = WiFi.RSSI();
    }
    return _lastSignalStrength;
}

bool WiFiHandler::setupAccessPoint(const char* ap_ssid, const char* ap_password) {
    String ssid = ap_ssid ? String(ap_ssid) : _ap_ssid;
    String password = ap_password ? String(ap_password) : _ap_password;

    DEBUG_PRINTLN("[WiFi] Setting up Access Point: " + ssid);

    WiFi.mode(WIFI_AP);
    bool success = WiFi.softAP(ssid.c_str(), password.c_str());

    if (success) {
        _currentState = WIFI_AP_MODE;
        _errorMessage = "";
        DEBUG_PRINTLN("[WiFi] Access Point created successfully");
        DEBUG_PRINTLN("[WiFi] AP IP: " + WiFi.softAPIP().toString());

#if ENABLE_MDNS
        if (_mdnsEnabled) {
            setupMDNS();
        }
#endif

        return true;
    } else {
        _errorMessage = "Failed to create Access Point";
        _currentState = WIFI_ERROR;
        return false;
    }
}

void WiFiHandler::setCredentials(const char* ssid, const char* password) {
    if (ssid && password) {
        _ssid = ssid;
        _password = password;
        _ap_ssid = String(ssid) + "_AP";
        _ap_password = password;
        DEBUG_PRINTLN("[WiFi] Credentials updated");
    }
}

void WiFiHandler::setReconnectionAttempts(int max_attempts) {
    _maxReconnectionAttempts = max_attempts;
}

void WiFiHandler::setReconnectionDelay(unsigned long initial_delay_ms) {
    _reconnectionDelay = initial_delay_ms;
}

void WiFiHandler::update() {
    _updateState();

    // Handle reconnection logic
    if (_currentState == WIFI_DISCONNECTED || _currentState == WIFI_ERROR) {
        _handleReconnection();
    }
}

void WiFiHandler::resetConnectionAttempts() {
    _currentReconnectionAttempt = 0;
    _lastReconnectionAttempt = 0;
}

#if ENABLE_MDNS
bool WiFiHandler::setupMDNS(const char* hostname) {
    if (!MDNS.begin(hostname)) {
        DEBUG_PRINTLN("[WiFi] MDNS setup failed");
        return false;
    }

    MDNS.addService("http", "tcp", 80);
    DEBUG_PRINTLN("[WiFi] MDNS setup complete: " + String(hostname) + ".local");
    _mdnsEnabled = true;
    return true;
}
#endif

#if ENABLE_OTA
bool WiFiHandler::setupOTA(const char* password) {
    ArduinoOTA.setHostname(MDNS_HOSTNAME);
    ArduinoOTA.setPassword(password);

    ArduinoOTA.onStart([]() {
        String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
        DEBUG_PRINTLN("[OTA] Start updating " + type);
    });

    ArduinoOTA.onEnd([]() {
        DEBUG_PRINTLN("[OTA] Update complete");
    });

    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        DEBUG_PRINTF("[OTA] Progress: %u%%\r", (progress / (total / 100)));
    });

    ArduinoOTA.onError([](ota_error_t error) {
        DEBUG_PRINTF("[OTA] Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR) DEBUG_PRINTLN("Auth Failed");
        else if (error == OTA_BEGIN_ERROR) DEBUG_PRINTLN("Begin Failed");
        else if (error == OTA_CONNECT_ERROR) DEBUG_PRINTLN("Connect Failed");
        else if (error == OTA_RECEIVE_ERROR) DEBUG_PRINTLN("Receive Failed");
        else if (error == OTA_END_ERROR) DEBUG_PRINTLN("End Failed");
    });

    ArduinoOTA.begin();
    DEBUG_PRINTLN("[OTA] OTA setup complete");
    _otaEnabled = true;
    return true;
}
#endif

// Private helper methods

bool WiFiHandler::_attemptConnection() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(_ssid.c_str(), _password.c_str());

    // Wait for connection with timeout
    int attempts = 0;
    const int max_attempts = 20;  // 20 * 500ms = 10 seconds timeout

    while (WiFi.status() != WL_CONNECTED && attempts < max_attempts) {
        delay(500);
        attempts++;

        if (attempts % 4 == 0) {  // Print status every 2 seconds
            DEBUG_PRINT(".");
        }
    }
    DEBUG_PRINTLN("");

    if (WiFi.status() == WL_CONNECTED) {
        _currentState = WIFI_CONNECTED;
        _connectionStartTime = millis();
        _currentReconnectionAttempt = 0;
        _errorMessage = "";

        DEBUG_PRINTLN("[WiFi] Connected successfully");
        DEBUG_PRINTLN("[WiFi] IP: " + WiFi.localIP().toString());
        DEBUG_PRINTF("[WiFi] Signal strength: %d dBm\n", WiFi.RSSI());

#if ENABLE_MDNS
        if (!_mdnsEnabled) {
            setupMDNS();
        }
#endif

#if ENABLE_OTA
        if (!_otaEnabled) {
            setupOTA();
        }
#endif

        // Setup web server and API endpoints
        setupWebServer();

        return true;
    } else {
        _errorMessage = _getWiFiErrorString(WiFi.status());
        _currentState = WIFI_DISCONNECTED;
        DEBUG_PRINTLN("[WiFi] Connection failed: " + _errorMessage);
        return false;
    }
}

void WiFiHandler::_updateState() {
    if (WiFi.getMode() == WIFI_AP) {
        if (_currentState != WIFI_AP_MODE) {
            _currentState = WIFI_AP_MODE;
        }
        return;
    }

    wl_status_t wifi_status = WiFi.status();

    switch (wifi_status) {
        case WL_CONNECTED:
            if (_currentState != WIFI_CONNECTED) {
                if (_connectionStartTime == 0) {
                    _connectionStartTime = millis();
                }
                _currentState = WIFI_CONNECTED;
                _currentReconnectionAttempt = 0;
                _errorMessage = "";
                DEBUG_PRINTLN("[WiFi] Connection established");
            }
            break;

        case WL_DISCONNECTED:
        case WL_CONNECTION_LOST:
        case WL_CONNECT_FAILED:
            if (_currentState == WIFI_CONNECTED) {
                _connectionStartTime = 0;
                DEBUG_PRINTLN("[WiFi] Connection lost");
            }
            _currentState = WIFI_DISCONNECTED;
            _errorMessage = _getWiFiErrorString(wifi_status);
            break;

        case WL_NO_SSID_AVAIL:
            _currentState = WIFI_ERROR;
            _errorMessage = "Network not found";
            break;

        default:
            if (_currentState != WIFI_CONNECTING) {
                _currentState = WIFI_DISCONNECTED;
                _errorMessage = _getWiFiErrorString(wifi_status);
            }
            break;
    }
}

void WiFiHandler::_handleReconnection() {
    if (_currentState == WIFI_CONNECTED || _currentState == WIFI_AP_MODE) {
        return;  // No need to reconnect
    }

    if (_currentReconnectionAttempt < _maxReconnectionAttempts) {
        reconnect();
    } else if (_currentState != WIFI_AP_MODE) {
        // All reconnection attempts failed, fall back to AP mode
        DEBUG_PRINTLN("[WiFi] All reconnection attempts failed, enabling AP mode");
        setupAccessPoint();
    }
}

bool WiFiHandler::_validateCredentials() {
    return (!_ssid.isEmpty() && !_password.isEmpty());
}

String WiFiHandler::_getWiFiErrorString(wl_status_t status) {
    switch (status) {
        case WL_NO_SHIELD: return "No WiFi shield";
        case WL_IDLE_STATUS: return "Idle";
        case WL_NO_SSID_AVAIL: return "Network not found";
        case WL_SCAN_COMPLETED: return "Scan completed";
        case WL_CONNECTED: return "Connected";
        case WL_CONNECT_FAILED: return "Connection failed";
        case WL_CONNECTION_LOST: return "Connection lost";
        case WL_DISCONNECTED: return "Disconnected";
        default: return "Unknown error (" + String(status) + ")";
    }
}

void WiFiHandler::setupWebServer() {
    // Note: Web server setup should be handled separately
    // This method is kept for backward compatibility but should be refactored
    // The web server should be created and managed outside WiFiHandler
    DEBUG_PRINTLN("[WiFi] Warning: setupWebServer() called - web server should be managed separately");
    DEBUG_PRINTLN("[WiFi] Please use setupApiEndpoints(WebServer*, BPMDetector*) directly");
    
    // For backward compatibility, still try to set up if server global exists
    if (server == nullptr) {
        DEBUG_PRINTLN("[WiFi] Web server not initialized - skipping setup");
        return;
    }

    // Setup API endpoints (will use globals)
    setupApiEndpoints();

    // Start the server
    server->begin();
    DEBUG_PRINTLN("[WiFi] Web server started on port " + String(SERVER_PORT));

    // Setup MDNS if not already done
#if ENABLE_MDNS
    if (MDNS.begin(MDNS_HOSTNAME)) {
        MDNS.addService("http", "tcp", SERVER_PORT);
        DEBUG_PRINTLN("[WiFi] MDNS responder started: http://" + String(MDNS_HOSTNAME) + ".local");
    }
#endif
}

unsigned long WiFiHandler::_calculateBackoffDelay() {
    // Exponential backoff: delay = base_delay * 2^attempt
    // Cap at 30 seconds maximum
    unsigned long delay = _reconnectionDelay * (1UL << min(_currentReconnectionAttempt, 5));
    return min(delay, 30000UL);
}