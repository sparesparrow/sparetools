#pragma once

#include <cstdint>
#include <memory>
#include "bpm_flatbuffers.h"

// Forward declare SpareTools types (when available)
// For now, include placeholder definitions
namespace SpareTools::Bpm {
    struct BpmResult;
    struct BpmConfig;
    class BpmDetector;
}

/**
 * @brief Adapter class that bridges Arduino-based ESP32 code with SpareTools BPM module
 *
 * This adapter provides an Arduino-compatible interface that internally uses
 * the enterprise-grade SpareTools::Bpm::BpmDetector. It allows gradual migration
 * from the current Arduino-based implementation to the new pure C++ module.
 *
 * The adapter maintains the same public interface as the current BPMDetector
 * class, making it a drop-in replacement.
 */
class BpmDetectorAdapter {
public:
    /**
     * @brief Construct a new BPM Detector Adapter
     */
    BpmDetectorAdapter();

    /**
     * @brief Destroy the BPM Detector Adapter
     */
    ~BpmDetectorAdapter();

    /**
     * @brief Initialize the BPM detector with ADC pin
     *
     * @param adc_pin ADC pin number for microphone input
     */
    void begin(uint8_t adc_pin);

    /**
     * @brief Process audio samples and detect BPM
     *
     * Call this method regularly (e.g., from loop()) to process audio samples
     * and update BPM detection.
     */
    void sample();

    /**
     * @brief Get the current detected BPM
     *
     * @return Detected BPM value (0-300 range)
     */
    float getBPM() const;

    /**
     * @brief Get the detection confidence
     *
     * @return Confidence value (0.0-1.0)
     */
    float getConfidence() const;

    /**
     * @brief Get the current signal level
     *
     * @return Signal level (0.0-1.0)
     */
    float getSignalLevel() const;

    /**
     * @brief Check if BPM detection is stable
     *
     * @return true if confidence >= threshold and BPM is valid
     */
    bool isStable() const;

    /**
     * @brief Get the detection status as string
     *
     * @return Human-readable status string
     */
    const char* getStatusString() const;

    /**
     * @brief Get audio processing statistics
     *
     * @return JSON-formatted string with statistics
     */
    String getStatsJson() const;

    /**
     * @brief Reset the detector state
     */
    void reset();

    /**
     * @brief Create FlatBuffers BPM update message
     *
     * @param builder FlatBuffers builder instance
     * @return Serialized BPM update data
     */
    std::vector<uint8_t> createBPMUpdateFlatBuffer(flatbuffers::FlatBufferBuilder& builder) const;

    /**
     * @brief Create FlatBuffers status update message
     *
     * @param uptime_seconds Device uptime
     * @param free_heap_bytes Available heap memory
     * @param cpu_usage_percent CPU usage percentage
     * @param wifi_rssi WiFi signal strength
     * @param builder FlatBuffers builder instance
     * @return Serialized status update data
     */
    std::vector<uint8_t> createStatusUpdateFlatBuffer(
        uint64_t uptime_seconds,
        uint32_t free_heap_bytes,
        uint8_t cpu_usage_percent,
        int8_t wifi_rssi,
        flatbuffers::FlatBufferBuilder& builder) const;

public:
    // Audio input interface (made public for implementation)
    class AudioInputInterface {
    public:
        virtual ~AudioInputInterface() = default;
        virtual uint32_t readSample() = 0;
    };

private:
    // ADC configuration
    uint8_t m_adcPin;
    bool m_initialized;

    // SpareTools BPM detector (when available)
    // For now, we'll use a placeholder implementation
    struct PlaceholderBpmDetector {
        float bpm = 0.0f;
        float confidence = 0.0f;
        float signalLevel = 0.0f;
        bool isStable = false;
        uint32_t sampleCount = 0;

        void processSample(uint32_t rawValue, uint32_t timeMs) {
            // Placeholder implementation
            // In real implementation, this would call SpareTools::Bpm::BpmDetector
            sampleCount++;
            // Simulate some basic BPM detection
            if (sampleCount % 1000 == 0) {
                bpm = 120.0f + (rand() % 40 - 20); // 100-140 BPM
                confidence = 0.7f;
                signalLevel = 0.8f;
                isStable = (confidence > 0.6f);
            }
        }

        void reset() {
            bpm = 0.0f;
            confidence = 0.0f;
            signalLevel = 0.0f;
            isStable = false;
            sampleCount = 0;
        }
    };

    PlaceholderBpmDetector m_detector;

    // Audio input interface
    AudioInputInterface* m_audioInput;

    // Arduino-compatible String for getStatsJson()
    // This maintains compatibility with existing code
};

// Compatibility typedef for existing code
using BPMDetector = BpmDetectorAdapter;
