#include "bpm_detector_adapter.h"
#include "audio_input.h"
#include <Arduino.h>

// Audio input implementation that uses the existing AudioInput class
class ArduinoAudioInput : public BpmDetectorAdapter::AudioInputInterface {
public:
    explicit ArduinoAudioInput(uint8_t adcPin) : m_adcPin(adcPin) {}

    uint32_t readSample() override {
        // Use existing AudioInput if available, otherwise use analogRead
        // For now, use analogRead for compatibility
        return analogRead(m_adcPin);
    }

private:
    uint8_t m_adcPin;
};

BpmDetectorAdapter::BpmDetectorAdapter()
    : m_adcPin(0)
    , m_initialized(false)
    , m_audioInput(nullptr) {
}

BpmDetectorAdapter::~BpmDetectorAdapter() {
    delete m_audioInput;
    m_audioInput = nullptr;
}

void BpmDetectorAdapter::begin(uint8_t adc_pin) {
    m_adcPin = adc_pin;
    m_audioInput = new ArduinoAudioInput(adc_pin);

    // Initialize ADC if needed
    analogReadResolution(12);  // 12-bit resolution

    m_initialized = true;
    m_detector.reset();
}

void BpmDetectorAdapter::sample() {
    if (!m_initialized || !m_audioInput) {
        return;
    }

    // Read audio sample
    uint32_t rawSample = m_audioInput->readSample();

    // Process with SpareTools detector (placeholder for now)
    uint32_t currentTime = millis();
    m_detector.processSample(rawSample, currentTime);
}

float BpmDetectorAdapter::getBPM() const {
    return m_detector.bpm;
}

float BpmDetectorAdapter::getConfidence() const {
    return m_detector.confidence;
}

float BpmDetectorAdapter::getSignalLevel() const {
    return m_detector.signalLevel;
}

bool BpmDetectorAdapter::isStable() const {
    return m_detector.isStable;
}

const char* BpmDetectorAdapter::getStatusString() const {
    if (!m_initialized) {
        return "NOT_INITIALIZED";
    }
    if (m_detector.isStable) {
        return "STABLE";
    }
    if (m_detector.signalLevel < 0.1f) {
        return "LOW_SIGNAL";
    }
    return "DETECTING";
}

String BpmDetectorAdapter::getStatsJson() const {
    // Create JSON-compatible string for existing code compatibility
    char buffer[256];
    snprintf(buffer, sizeof(buffer),
             "{\"bpm\":%.1f,\"confidence\":%.2f,\"signalLevel\":%.2f,\"isStable\":%s,\"sampleCount\":%u}",
             m_detector.bpm,
             m_detector.confidence,
             m_detector.signalLevel,
             m_detector.isStable ? "true" : "false",
             m_detector.sampleCount);
    return String(buffer);
}

void BpmDetectorAdapter::reset() {
    m_detector.reset();
}

std::vector<uint8_t> BpmDetectorAdapter::createBPMUpdateFlatBuffer(
    flatbuffers::FlatBufferBuilder& builder) const {

    // Use existing FlatBuffers implementation directly
    auto bpmUpdateOffset = BPMFlatBuffers::createBPMUpdate(m_detector.bpm, m_detector.confidence,
                                                          m_detector.signalLevel,
                                                          sparesparrow::bpm::DetectionStatus::DETECTING,
                                                          builder);

    return BPMFlatBuffers::serializeBPMUpdate(bpmUpdateOffset, builder);
}

std::vector<uint8_t> BpmDetectorAdapter::createStatusUpdateFlatBuffer(
    uint64_t uptime_seconds,
    uint32_t free_heap_bytes,
    uint8_t cpu_usage_percent,
    int8_t wifi_rssi,
    flatbuffers::FlatBufferBuilder& builder) const {

    // Create status update using existing FlatBuffers implementation
    auto statusUpdateOffset = BPMFlatBuffers::createStatusUpdate(uptime_seconds,
                                                                 free_heap_bytes,
                                                                 cpu_usage_percent,
                                                                 wifi_rssi,
                                                                 builder);

    return BPMFlatBuffers::serializeStatusUpdate(statusUpdateOffset, builder);
}
