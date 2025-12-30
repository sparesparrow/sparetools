/**
 * {{cookiecutter.project_name}} - ESP32 Firmware
 *
 * {{cookiecutter.project_short_description}}
 *
 * Generated from SpareTools ESP32 template
 * Author: {{cookiecutter.author}}
 * Version: {{cookiecutter.version}}
 */

#include <Arduino.h>
{% if cookiecutter.include_wifi == 'y' %}
#include <WiFi.h>
#include <WebServer.h>
{% endif %}
{% if cookiecutter.include_websocket == 'y' %}
#include <WebSocketsServer.h>
{% endif %}
{% if cookiecutter.include_display == 'y' %}
#include <Wire.h>
#include <Adafruit_SSD1306.h>
{% endif %}

{% if cookiecutter.schema_component != 'none' %}
// SpareTools Protocol Headers
#include "{{cookiecutter.schema_component|upper}}_generated.h"

// Protocol namespace
using namespace sparesparrow::{{cookiecutter.schema_component}};
{% endif %}

// Configuration
#define WIFI_SSID "{{cookiecutter.project_slug|upper}}_AP"
#define WIFI_PASSWORD "password123"
#define WEBSERVER_PORT 80
#define WEBSOCKET_PORT 81

{% if cookiecutter.include_wifi == 'y' %}
// Web server and WebSocket server
WebServer server(WEBSERVER_PORT);
{% endif %}
{% if cookiecutter.include_websocket == 'y' %}
WebSocketsServer webSocket(WEBSOCKET_PORT);
{% endif %}

{% if cookiecutter.include_display == 'y' %}
// OLED Display
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
{% endif %}

{% if cookiecutter.schema_component != 'none' %}
// FlatBuffers builder for protocol messages
flatbuffers::FlatBufferBuilder fbb;
{% endif %}

void setup() {
    Serial.begin(115200);
    Serial.println("{{cookiecutter.project_name}} - Starting up...");

    {% if cookiecutter.include_display == 'y' %}
    // Initialize OLED display
    if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("SSD1306 allocation failed");
        for(;;);
    }
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,0);
    display.println("{{cookiecutter.project_name}}");
    display.println("Starting...");
    display.display();
    {% endif %}

    {% if cookiecutter.include_wifi == 'y' %}
    // Initialize WiFi
    WiFi.softAP(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("WiFi AP started: ");
    Serial.println(WIFI_SSID);
    Serial.print("IP Address: ");
    Serial.println(WiFi.softAPIP());

    {% if cookiecutter.include_display == 'y' %}
    display.println("WiFi: " + String(WIFI_SSID));
    display.println("IP: " + WiFi.softAPIP().toString());
    display.display();
    {% endif %}

    // Setup web server routes
    server.on("/", HTTP_GET, []() {
        String html = "<html><body>";
        html += "<h1>{{cookiecutter.project_name}}</h1>";
        html += "<p>{{cookiecutter.project_short_description}}</p>";
        html += "<p>IP: " + WiFi.softAPIP().toString() + "</p>";
        html += "</body></html>";
        server.send(200, "text/html", html);
    });

    server.begin();
    Serial.println("Web server started on port " + String(WEBSERVER_PORT));
    {% endif %}

    {% if cookiecutter.include_websocket == 'y' %}
    // Initialize WebSocket server
    webSocket.begin();
    webSocket.onEvent(onWebSocketEvent);
    Serial.println("WebSocket server started on port " + String(WEBSOCKET_PORT));
    {% endif %}

    Serial.println("{{cookiecutter.project_name}} initialization complete!");
    {% if cookiecutter.include_display == 'y' %}
    display.println("Ready!");
    display.display();
    {% endif %}
}

{% if cookiecutter.include_websocket == 'y' %}
void onWebSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[%u] Disconnected!\n", num);
            break;
        case WStype_CONNECTED: {
            IPAddress ip = webSocket.remoteIP(num);
            Serial.printf("[%u] Connected from %d.%d.%d.%d\n", num, ip[0], ip[1], ip[2], ip[3]);
            break;
        }
        case WStype_TEXT:
            Serial.printf("[%u] Text: %s\n", num, payload);
            break;
        case WStype_BIN:
            Serial.printf("[%u] Binary data received\n", num);
            break;
    }
}
{% endif %}

{% if cookiecutter.schema_component != 'none' %}
// Protocol message creation functions
{% if cookiecutter.schema_component == 'bpm' %}
flatbuffers::Offset<BPMUpdate> createBPMUpdate(float bpm, float confidence) {
    return CreateBPMUpdate(fbb,
                          bpm,
                          confidence,
                          0.8f, // signal_level
                          DetectionStatus_DETECTING,
                          0, // analysis (placeholder)
                          0, // quality (placeholder)
                          millis());
}
{% endif %}
{% endif %}

void loop() {
    {% if cookiecutter.include_wifi == 'y' %}
    server.handleClient();
    {% endif %}

    {% if cookiecutter.include_websocket == 'y' %}
    webSocket.loop();
    {% endif %}

    {% if cookiecutter.schema_component == 'bpm' %}
    // Example: Send BPM data every 100ms
    static unsigned long lastUpdate = 0;
    if (millis() - lastUpdate > 100) {
        // Simulate BPM data
        float bpm = 120.0f + random(-10, 10);
        float confidence = 0.85f;

        {% if cookiecutter.include_websocket == 'y' %}
        // Create and send FlatBuffers message
        fbb.Clear();
        auto bpmUpdate = createBPMUpdate(bpm, confidence);
        fbb.Finish(bpmUpdate);

        webSocket.broadcastBIN(fbb.GetBufferPointer(), fbb.GetSize());
        {% endif %}

        {% if cookiecutter.include_display == 'y' %}
        display.clearDisplay();
        display.setCursor(0,0);
        display.printf("BPM: %.1f\n", bpm);
        display.printf("Conf: %.1f%%\n", confidence * 100);
        display.display();
        {% endif %}

        lastUpdate = millis();
    }
    {% endif %}

    delay(10);
}




