/**
 * @file bpm_integration.h
 * @brief BPM Protocol Integration for NucleusESP32
 *
 * This header demonstrates how NucleusESP32 can integrate SpareTools BPM protocols
 * for audio processing features. This is an example integration showing how
 * the BPM (Beat Processing Module) schemas can be used alongside NucleusESP32's
 * existing protocol system.
 */

#ifndef BPM_INTEGRATION_H
#define BPM_INTEGRATION_H

#include <Arduino.h>

// SpareTools BPM Protocol Headers (available via Conan)
// Note: These would be available after running conan install
#include "sparesparrow/bpm/BPM_generated.h"
#include "sparesparrow/bpm/common_generated.h"

// Forward declarations for BPM integration
namespace nucleus {
namespace bpm {

/**
 * @brief BPM Audio Processor for NucleusESP32
 *
 * Example integration showing how BPM protocols can be used
 * for audio processing within NucleusESP32's architecture.
 */
class BPMAudioProcessor {
public:
    BPMAudioProcessor();
    ~BPMAudioProcessor();

    /**
     * Process audio sample and create BPM update message
     * @param audio_sample Raw audio sample
     * @param sample_rate Sample rate in Hz
     * @return BPM update message (FlatBuffers)
     */
    std::vector<uint8_t> processAudioSample(int16_t audio_sample, uint32_t sample_rate);

    /**
     * Get current BPM analysis results
     * @return BPM analysis data
     */
    sparesparrow::bpm::BPMAnalysis getBPMAnalysis() const;

    /**
     * Create status update message
     * @param bpm Current BPM value
     * @param confidence Detection confidence (0.0-1.0)
     * @return Status update message
     */
    std::vector<uint8_t> createStatusUpdate(float bpm, float confidence);

private:
    // Internal BPM processing state
    float current_bpm_;
    float confidence_;
    uint32_t sample_count_;
    uint64_t last_update_time_;

    // BPM analysis data
    float stability_;
    float regularity_;
    float dominant_frequency_;
    float spectral_centroid_;
    float beat_position_;
    float tempo_consistency_;
};

/**
 * @brief BPM Protocol Handler
 *
 * Handles communication between NucleusESP32 and external BPM clients
 * using the SpareTools BPM protocol schemas.
 */
class BPMProtocolHandler {
public:
    BPMProtocolHandler();
    ~BPMProtocolHandler();

    /**
     * Process incoming BPM protocol message
     * @param message Raw message bytes
     * @return Response message (if any)
     */
    std::vector<uint8_t> processMessage(const std::vector<uint8_t>& message);

    /**
     * Send BPM update to connected clients
     * @param bpm BPM value
     * @param confidence Confidence level
     * @param timestamp Message timestamp
     */
    void sendBPMUpdate(float bpm, float confidence, uint64_t timestamp);

    /**
     * Send status update
     * @param status Current system status
     */
    void sendStatusUpdate(sparesparrow::bpm::DetectionStatus status);

private:
    // Protocol state
    uint32_t next_message_id_;
    BPMAudioProcessor* audio_processor_;

    // Message buffers
    flatbuffers::FlatBufferBuilder builder_;
};

} // namespace bpm
} // namespace nucleus

#endif // BPM_INTEGRATION_H

