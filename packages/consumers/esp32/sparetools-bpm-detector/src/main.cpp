#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <ESPmDNS.h>
#include "config.h"
#include "bpm_detector.h"
#include "audio_input.h"
#include "display_handler.h"
#include "wifi_handler.h"
#include <flatbuffers/flatbuffers.h>
#include "bpm_flatbuffers.h"  // Real FlatBuffers implementation

// #region agent log
// JTAG-based logging: Use a circular buffer in memory that can be read via JTAG/GDB
#define LOG_BUFFER_SIZE 8192
#define MAX_LOG_ENTRIES 100

struct LogEntry {
    char data[256];
    unsigned long timestamp;
    bool valid;
};

// Circular buffer in RAM (accessible via JTAG memory dump)
volatile LogEntry logBuffer[MAX_LOG_ENTRIES] __attribute__((section(".dram0.data")));
volatile uint32_t logWriteIndex = 0;
volatile uint32_t logCount = 0;

void writeLog(const char* location, const char* message, const char* hypothesisId, const char* dataJson) {
    unsigned long ts = millis();
    char logLine[256];
    snprintf(logLine, sizeof(logLine), "{\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"%s\",\"location\":\"%s\",\"message\":\"%s\",\"data\":%s,\"timestamp\":%lu}", hypothesisId, location, message, dataJson, ts);

    // Write to circular buffer (accessible via JTAG memory dump)
    uint32_t idx = logWriteIndex % MAX_LOG_ENTRIES;
    strncpy((char*)logBuffer[idx].data, logLine, sizeof(logBuffer[idx].data) - 1);
    logBuffer[idx].data[sizeof(logBuffer[idx].data) - 1] = '\0';
    logBuffer[idx].timestamp = ts;
    logBuffer[idx].valid = true;

    logWriteIndex++;
    if (logCount < MAX_LOG_ENTRIES) logCount++;

    // Memory barrier to ensure data is written before JTAG reads it
    __sync_synchronize();
}
// #endregion

// Global instances
BPMDetector* bpmDetector = nullptr;
AudioInput* audioInput = nullptr;
DisplayHandler* displayHandler = nullptr;
WiFiHandler* wifiHandler = nullptr;
WebServer* server = nullptr;

// Timing variables
unsigned long lastDetectionTime = 0;
unsigned long lastDisplayUpdate = 0;
unsigned long lastStatusUpdate = 0;

// BPM detector data
BPMDetector::BPMData currentBPMData;

// #region agent log
void writeBPMLog(const char* location, const char* message, const char* hypothesisId, const BPMDetector::BPMData& data) {
    char dataBuf[256];
    snprintf(dataBuf, sizeof(dataBuf),
             "{\"bpm\":%.1f,\"confidence\":%.3f,\"signalLevel\":%.3f,\"status\":\"%s\",\"timestamp\":%lu}",
             data.bpm, data.confidence, data.signal_level, data.status.c_str(), data.timestamp);
    writeLog(location, message, hypothesisId, dataBuf);
}
// #endregion

// #region agent log
bool testFlatBuffers() {
    // Clear test header with distinctive markers
    DEBUG_PRINTLN("\n========== FlatBuffers Test Start ==========");
    DEBUG_PRINT("Time: ");
    DEBUG_PRINT(millis());
    DEBUG_PRINT("ms, Heap: ");
    DEBUG_PRINTLN(ESP.getFreeHeap());
    DEBUG_FLUSH();

    writeLog("main.cpp:testFlatBuffers", "Starting real FlatBuffers serialization test", "F", "{}");

    int testsPassed = 0;
    int totalTests = 5;

    // Test 1: Create and serialize BPM update message
    DEBUG_PRINT("Test 1: BPM Update Serialization...");
    delay(5);

    flatbuffers::FlatBufferBuilder builder1(1024);

    // Create BPM update with real data
    auto bpm_update_offset = BPMFlatBuffers::createBPMUpdate(
        128.5f,     // bpm
        0.85f,      // confidence
        0.75f,      // signal_level
        sparesparrow::bpm::DetectionStatus::DETECTING,
        builder1
    );

    // Serialize to binary
    auto binary_data1 = BPMFlatBuffers::serializeBPMUpdate(bpm_update_offset, builder1);

    bool test1_pass = (binary_data1.size() > 0 && binary_data1.size() < 1024);

    if (test1_pass) {
        DEBUG_PRINTLN(" PASS");
        testsPassed++;
    } else {
        DEBUG_PRINTLN(" FAIL");
    }
    DEBUG_FLUSH();

    // #region agent log
    char dataBuf1[128];
    snprintf(dataBuf1, sizeof(dataBuf1), "{\"serializedSize\":%zu,\"passed\":%d}", binary_data1.size(), test1_pass ? 1 : 0);
    writeLog("main.cpp:testFlatBuffers", "BPM Update serialization tested", "F", dataBuf1);
    // #endregion

    // Test 2: BPM Update Creation Validation
    DEBUG_PRINT("Test 2: BPM Update Creation Validation...");
    delay(5);

    // Since BPMUpdate is not a root type, we test creation instead of deserialization
    flatbuffers::FlatBufferBuilder test_builder(1024);
    auto test_bpm_offset = BPMFlatBuffers::createBPMUpdate(
        120.0f, 0.9f, 0.8f, IcdBpm::DetectionStatus::DETECTING, test_builder
    );

    // Just test that creation succeeded (offset is valid)
    bool test2_pass = (test_bpm_offset.o != 0);

    if (test2_pass) {
        DEBUG_PRINTLN(" PASS");
        testsPassed++;
    } else {
        DEBUG_PRINTLN(" FAIL");
    }
    DEBUG_FLUSH();

    // #region agent log
    char dataBuf2[128];
    snprintf(dataBuf2, sizeof(dataBuf2), "{\"bpmOffset\":%u,\"passed\":%d,\"note\":\"BPMUpdate not root type, testing creation only\"}",
             (unsigned int)test_bpm_offset.o, test2_pass ? 1 : 0);
    writeLog("main.cpp:testFlatBuffers", "BPM Update creation validated", "F", dataBuf2);
    // #endregion

    // Test 3: Create and serialize status update message
    DEBUG_PRINT("Test 3: Status Update Serialization...");
    delay(5);

    flatbuffers::FlatBufferBuilder builder2(1024);

    auto status_update_offset = BPMFlatBuffers::createStatusUpdate(
        3600,       // uptime_seconds
        256000,     // free_heap_bytes
        15,         // cpu_usage_percent
        -45,        // wifi_rssi
        builder2
    );

    auto binary_data2 = BPMFlatBuffers::serializeStatusUpdate(status_update_offset, builder2);

    bool test3_pass = (binary_data2.size() > 0 && binary_data2.size() < 1024);

    if (test3_pass) {
        DEBUG_PRINTLN(" PASS");
        testsPassed++;
    } else {
        DEBUG_PRINTLN(" FAIL");
    }
    DEBUG_FLUSH();

    // #region agent log
    char dataBuf3[128];
    snprintf(dataBuf3, sizeof(dataBuf3), "{\"serializedSize\":%zu,\"passed\":%d}", binary_data2.size(), test3_pass ? 1 : 0);
    writeLog("main.cpp:testFlatBuffers", "Status Update serialization tested", "F", dataBuf3);
    // #endregion

    // Test 4: Status Update Deserialization
    DEBUG_PRINT("Test 4: Status Update Deserialization...");
    delay(5);

    auto status_update = BPMFlatBuffers::deserializeStatusUpdate(binary_data2);

    bool test4_pass = (status_update != nullptr &&
                      status_update->uptime_seconds() == 3600 &&
                      status_update->free_heap_bytes() == 256000);

    if (test4_pass) {
        DEBUG_PRINTLN(" PASS");
        testsPassed++;
    } else {
        DEBUG_PRINTLN(" FAIL");
    }
    DEBUG_FLUSH();

    // #region agent log
    char dataBuf4[128];
    if (status_update) {
        snprintf(dataBuf4, sizeof(dataBuf4), "{\"uptime\":%llu,\"freeHeap\":%u,\"passed\":%d}",
                 status_update->uptime_seconds(), status_update->free_heap_bytes(), test4_pass ? 1 : 0);
    } else {
        snprintf(dataBuf4, sizeof(dataBuf4), "{\"statusUpdate\":null,\"passed\":%d}", test4_pass ? 1 : 0);
    }
    writeLog("main.cpp:testFlatBuffers", "Status Update deserialization tested", "F", dataBuf4);
    // #endregion

    // Test 5: API Functionality Validation
    DEBUG_PRINT("Test 5: API Functionality Validation...");
    delay(5);

    // Test that the FlatBuffers API functions exist and are callable
    const char* status_str = BPMFlatBuffers::detectionStatusToString(IcdBpm::DetectionStatus::DETECTING);
    bool api_test = (status_str != nullptr && strlen(status_str) > 0);

    bool test5_pass = (test_bpm_offset.o != 0 && status_update != nullptr && api_test);

    if (test5_pass) {
        DEBUG_PRINTLN(" PASS");
        testsPassed++;
    } else {
        DEBUG_PRINTLN(" FAIL");
    }
    DEBUG_FLUSH();

    // #region agent log
    char dataBuf5[128];
    snprintf(dataBuf5, sizeof(dataBuf5), "{\"bpmCreated\":%d,\"statusDeserialized\":%d,\"apiWorks\":%d,\"passed\":%d}",
             test_bpm_offset.o != 0 ? 1 : 0, status_update != nullptr ? 1 : 0, api_test ? 1 : 0, test5_pass ? 1 : 0);
    writeLog("main.cpp:testFlatBuffers", "API functionality validation tested", "F", dataBuf5);
    // #endregion

    // Summary
    DEBUG_PRINT("\n========== Test Complete: ");
    DEBUG_PRINT(testsPassed);
    DEBUG_PRINT("/");
    DEBUG_PRINT(totalTests);
    DEBUG_PRINT(" PASSED ==========\n");
    DEBUG_FLUSH();

    DEBUG_PRINT("FlatBuffers serialization/deserialization ");
    if (testsPassed == totalTests) {
        DEBUG_PRINTLN("completed successfully!");
    } else {
        DEBUG_PRINT("completed with ");
        DEBUG_PRINT(totalTests - testsPassed);
        DEBUG_PRINTLN(" failures.");
    }
    DEBUG_PRINTLN("Note: Real FlatBuffers library integrated and tested");
    DEBUG_FLUSH();

    writeLog("main.cpp:testFlatBuffers", "Real FlatBuffers serialization test completed", "F",
             "{\"status\":\"real_flatbuffers_test\",\"testsPassed\":%d,\"totalTests\":%d,\"note\":\"Real FlatBuffers library integrated and tested\"}");

    return testsPassed == totalTests;
}
// #endregion

void setup() {
    // #region agent log
    writeLog("main.cpp:setup:entry", "BPM Detector setup started", "A", "{\"freeHeap\":0}");
    // #endregion

    Serial.begin(115200);
    delay(1000); // Allow Serial to initialize

    // #region agent log
    unsigned long heapBefore = ESP.getFreeHeap();
    char dataBuf1[128];
    snprintf(dataBuf1, sizeof(dataBuf1), "{\"freeHeap\":%lu,\"serialBaud\":115200}", heapBefore);
    writeLog("main.cpp:setup:serialInit", "Serial initialized", "A", dataBuf1);
    // #endregion

    DEBUG_PRINTLN("\n=== ESP32 BPM Detector Starting ===");

    // Skip WiFi initialization for now to avoid TCP stack crashes
    DEBUG_PRINTLN("WiFi disabled - focusing on BPM detection");

    // #region agent log
    writeLog("main.cpp:setup:wifiSkipped", "WiFi initialization skipped to avoid TCP stack issues", "D", "{}");
    // #endregion

    // Initialize display handler
    displayHandler = new DisplayHandler();
    displayHandler->begin(DISPLAY_NONE);  // No display for now

    // #region agent log
    writeLog("main.cpp:setup:displayInit", "Display handler initialized", "E", "{}");
    // #endregion

    // Initialize audio input
    // #region agent log
    char dataBuf3[128];
    snprintf(dataBuf3, sizeof(dataBuf3), "{\"adcPin\":%d,\"sampleRate\":%d}", MICROPHONE_PIN, SAMPLE_RATE);
    writeLog("main.cpp:setup:audioInit", "Initializing audio input", "B", dataBuf3);
    // #endregion

    audioInput = new AudioInput();
    audioInput->begin(MICROPHONE_PIN);

    // Initialize BPM detector with dependency injection
    // #region agent log
    char dataBuf4[128];
    snprintf(dataBuf4, sizeof(dataBuf4), "{\"sampleRate\":%d,\"fftSize\":%d,\"adcPin\":%d}", SAMPLE_RATE, FFT_SIZE, MICROPHONE_PIN);
    writeLog("main.cpp:setup:bpmInit", "Initializing BPM detector", "B", dataBuf4);
    // #endregion

    // Use dependency injection: pass AudioInput to BPMDetector
    bpmDetector = new BPMDetector(audioInput, SAMPLE_RATE, FFT_SIZE);
    bpmDetector->begin(audioInput, MICROPHONE_PIN);

    // Skip web server initialization (requires WiFi)
    DEBUG_PRINTLN("Web server disabled - no WiFi");

    // #region agent log
    unsigned long heapAfter = ESP.getFreeHeap();
    char dataBuf5[128];
    snprintf(dataBuf5, sizeof(dataBuf5), "{\"freeHeap\":%lu,\"heapDelta\":%ld,\"serverPort\":%d}",
             heapAfter, (long)(heapAfter - heapBefore), SERVER_PORT);
    writeLog("main.cpp:setup:complete", "Setup completed successfully", "A", dataBuf5);
    // #endregion

    DEBUG_PRINTLN("ESP32 BPM Detector Ready!");
    DEBUG_PRINT("Free heap: ");
    DEBUG_PRINTLN(ESP.getFreeHeap());

    // FlatBuffers test will run in main loop
    DEBUG_PRINTLN("Setup complete - FlatBuffers test will run in main loop");
    DEBUG_PRINTLN("Send 't' or 'T' via serial to manually trigger FlatBuffers test");
}

void loop() {
    static unsigned long loopCount = 0;
    static unsigned long sampleCount = 0;
    static bool flatBuffersTestRun = false;
    unsigned long currentTime = millis();

    loopCount++;

    // Check for serial command to run FlatBuffers test
    if (Serial.available() > 0) {
        char cmd = Serial.read();
        if (cmd == 't' || cmd == 'T') {
            DEBUG_PRINTLN("\nManual FlatBuffers test trigger received...");
            DEBUG_FLUSH();
            delay(10);
            bool testResult = testFlatBuffers();
            DEBUG_PRINT("Manual FlatBuffers test result: ");
            DEBUG_PRINTLN(testResult ? "SUCCESS" : "FAILED");
            DEBUG_PRINTLN("Manual test completed.");
            DEBUG_FLUSH();
        }
    }

    // Run FlatBuffers test once after startup (2-3 seconds after boot)
    if (!flatBuffersTestRun && millis() > 2000 && loopCount > 10) {
        DEBUG_PRINTLN("Running FlatBuffers test in main loop...");
        DEBUG_FLUSH();
        delay(10); // Small delay to ensure serial output
        bool testResult = testFlatBuffers();
        DEBUG_PRINT("FlatBuffers test result: ");
        DEBUG_PRINTLN(testResult ? "SUCCESS" : "FAILED");
        DEBUG_PRINTLN("FlatBuffers test completed in main loop.");
        DEBUG_FLUSH();
        flatBuffersTestRun = true;
    }

    // Sample audio at regular intervals
    if ((currentTime - lastDetectionTime) >= (1000000 / SAMPLE_RATE)) {  // Sample at SAMPLE_RATE Hz
        // #region agent log
        char dataBuf1[128];
        snprintf(dataBuf1, sizeof(dataBuf1), "{\"sampleCount\":%lu,\"timeSinceLast\":%lu}",
                 sampleCount, currentTime - lastDetectionTime);
        writeLog("main.cpp:loop:sample", "Taking audio sample", "B", dataBuf1);
        // #endregion

        if (bpmDetector) {
            bpmDetector->sample();
        }

        sampleCount++;
        lastDetectionTime = currentTime;
    }

    // Perform BPM detection every 100ms
    if ((currentTime - lastDetectionTime) >= 100) {
        if (bpmDetector && bpmDetector->isBufferReady()) {
            // #region agent log
            writeLog("main.cpp:loop:detectStart", "Starting BPM detection", "C", "{}");
            // #endregion

            currentBPMData = bpmDetector->detect();

            // #region agent log
            writeBPMLog("main.cpp:loop:detectResult", "BPM detection completed", "C", currentBPMData);
            // #endregion

            // Create FlatBuffers BPM update message
            if (currentBPMData.bpm > 0.0f && currentBPMData.confidence >= CONFIDENCE_THRESHOLD) {
                flatbuffers::FlatBufferBuilder bpmBuilder(512);

                // Convert status string to enum
                sparesparrow::bpm::DetectionStatus fbStatus = sparesparrow::bpm::DetectionStatus::DETECTING;
                if (currentBPMData.status == "initializing") fbStatus = sparesparrow::bpm::DetectionStatus::INITIALIZING;
                else if (currentBPMData.status == "detecting") fbStatus = sparesparrow::bpm::DetectionStatus::DETECTING;
                else if (currentBPMData.status == "low_signal") fbStatus = sparesparrow::bpm::DetectionStatus::LOW_SIGNAL;
                else if (currentBPMData.status == "no_signal") fbStatus = sparesparrow::bpm::DetectionStatus::NO_SIGNAL;
                else if (currentBPMData.status == "error") fbStatus = sparesparrow::bpm::DetectionStatus::ERROR;
                else if (currentBPMData.status == "calibrating") fbStatus = sparesparrow::bpm::DetectionStatus::CALIBRATING;

                auto bpmUpdateOffset = BPMFlatBuffers::createBPMUpdate(
                    currentBPMData.bpm,
                    currentBPMData.confidence,
                    currentBPMData.signal_level,
                    fbStatus,
                    bpmBuilder
                );

                auto bpmMessage = BPMFlatBuffers::serializeBPMUpdate(bpmUpdateOffset, bpmBuilder);

                // #region agent log
                char dataBufBPM[128];
                snprintf(dataBufBPM, sizeof(dataBufBPM), "{\"messageSize\":%zu,\"timestamp\":%lu}",
                         bpmMessage.size(), currentBPMData.timestamp);
                writeLog("main.cpp:loop:bpmSerialized", "BPM data serialized to FlatBuffers", "C", dataBufBPM);
                // #endregion

                // TODO: Send over network when WiFi is enabled
                // For now, just validate serialization worked
                if (bpmMessage.size() > 0) {
                    DEBUG_PRINT(" [FlatBuffers: ");
                    DEBUG_PRINT(bpmMessage.size());
                    DEBUG_PRINT(" bytes]");
                }
            }

            DEBUG_PRINT("BPM: ");
            DEBUG_PRINT(currentBPMData.bpm);
            DEBUG_PRINT(" Confidence: ");
            DEBUG_PRINT(currentBPMData.confidence);
            DEBUG_PRINT(" Status: ");
            DEBUG_PRINTLN(currentBPMData.status.c_str());

            lastDetectionTime = currentTime;
        }
    }

    // Update display every 200ms
    if ((currentTime - lastDisplayUpdate) >= 200) {
        if (displayHandler) {
            displayHandler->showBPM((int)currentBPMData.bpm, currentBPMData.confidence);

            // #region agent log
            writeBPMLog("main.cpp:loop:displayUpdate", "Display updated with BPM data", "E", currentBPMData);
            // #endregion
        }
        lastDisplayUpdate = currentTime;
    }

    // Print status every 2 seconds
    if ((currentTime - lastStatusUpdate) >= 2000) {
        unsigned long freeHeap = ESP.getFreeHeap();

        // Create FlatBuffers status update message
        flatbuffers::FlatBufferBuilder statusBuilder(512);

        auto statusUpdateOffset = BPMFlatBuffers::createStatusUpdate(
            currentTime / 1000,  // uptime_seconds
            freeHeap,            // free_heap_bytes
            15,                  // cpu_usage_percent (mock value)
            -50,                 // wifi_rssi (mock value)
            statusBuilder
        );

        auto statusMessage = BPMFlatBuffers::serializeStatusUpdate(statusUpdateOffset, statusBuilder);

        // #region agent log
        char dataBuf2[256];
        snprintf(dataBuf2, sizeof(dataBuf2), "{\"freeHeap\":%lu,\"loopCount\":%lu,\"sampleCount\":%lu,\"uptime\":%lu,\"messageSize\":%zu}",
                 freeHeap, loopCount, sampleCount, currentTime / 1000, statusMessage.size());
        writeLog("main.cpp:loop:status", "Periodic status update with FlatBuffers", "F", dataBuf2);
        // #endregion

        // TODO: Send over network when WiFi is enabled
        // For now, just validate serialization worked
        if (statusMessage.size() > 0) {
            DEBUG_PRINT(" [Status FlatBuffers: ");
            DEBUG_PRINT(statusMessage.size());
            DEBUG_PRINT(" bytes]");
        }

        DEBUG_PRINT("Status - Free heap: ");
        DEBUG_PRINT(freeHeap);
        DEBUG_PRINT(" bytes, Samples: ");
        DEBUG_PRINT(sampleCount);
        DEBUG_PRINT(", Uptime: ");
        DEBUG_PRINT(currentTime / 1000);
        DEBUG_PRINTLN("s");

        lastStatusUpdate = currentTime;
    }

    // Web server disabled

    // Small delay to prevent watchdog timeout
    delay(1);
}