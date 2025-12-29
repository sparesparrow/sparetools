/**
 * @file bpm_integration.cpp
 * @brief BPM Protocol Integration Implementation
 *
 * Example implementation showing how NucleusESP32 can integrate
 * SpareTools BPM protocols for audio processing features.
 */

#include "bpm_integration.h"
#include <flatbuffers/flatbuffers.h>

namespace nucleus {
namespace bpm {

// BPMAudioProcessor Implementation
BPMAudioProcessor::BPMAudioProcessor()
    : current_bpm_(0.0f)
    , confidence_(0.0f)
    , sample_count_(0)
    , last_update_time_(0)
    , stability_(0.8f)
    , regularity_(0.7f)
    , dominant_frequency_(440.0f)
    , spectral_centroid_(0.6f)
    , beat_position_(0.3f)
    , tempo_consistency_(0.8f)
{
}

BPMAudioProcessor::~BPMAudioProcessor() {
}

std::vector<uint8_t> BPMAudioProcessor::processAudioSample(int16_t audio_sample, uint32_t sample_rate) {
    // Simple BPM detection algorithm (placeholder)
    // In a real implementation, this would analyze the audio signal
    // to detect beats and calculate BPM

    sample_count_++;

    // Simulate BPM detection every 1000 samples
    if (sample_count_ % 1000 == 0) {
        // Mock BPM calculation
        current_bpm_ = 120.0f + (rand() % 40) - 20; // 100-140 BPM range
        confidence_ = 0.8f + (rand() % 20) / 100.0f; // 0.8-1.0 confidence

        // Update analysis metrics
        stability_ = 0.75f + (rand() % 25) / 100.0f;
        regularity_ = 0.7f + (rand() % 30) / 100.0f;
        dominant_frequency_ = 400.0f + (rand() % 80); // 400-480 Hz
        spectral_centroid_ = 0.5f + (rand() % 50) / 100.0f;
        beat_position_ = (rand() % 100) / 100.0f;
        tempo_consistency_ = 0.75f + (rand() % 25) / 100.0f;

        last_update_time_ = millis();
    }

    // Create BPM update message using SpareTools BPM schema
    flatbuffers::FlatBufferBuilder builder;

    // Create BPM analysis data
    auto analysis_offset = sparesparrow::bpm::CreateBPMAnalysis(
        builder,
        stability_,
        regularity_,
        dominant_frequency_,
        spectral_centroid_,
        beat_position_,
        tempo_consistency_
    );

    // Create BPM update
    auto bpm_update_offset = sparesparrow::bpm::CreateBPMUpdate(
        builder,
        current_bpm_,
        confidence_,
        0.75f, // signal_level
        sparesparrow::bpm::DetectionStatus_DETECTED, // status
        analysis_offset
    );

    // Create message envelope
    auto envelope_offset = sparesparrow::bpm::CreateHeader(
        builder,
        sparesparrow::bpm::MessageType_BPM_UPDATE,
        last_update_time_,
        1, // message_id
        sparesparrow::bpm::CreateMessagePayload(builder, sparesparrow::bpm::Payload_BPMUpdate, bpm_update_offset.Union())
    );

    builder.Finish(envelope_offset);

    // Return serialized message
    return std::vector<uint8_t>(builder.GetBufferPointer(), builder.GetBufferPointer() + builder.GetSize());
}

sparesparrow::bpm::BPMAnalysis BPMAudioProcessor::getBPMAnalysis() const {
    // Return current analysis data
    // Note: In a real implementation, this would return actual analysis results
    return sparesparrow::bpm::BPMAnalysis(
        stability_,
        regularity_,
        dominant_frequency_,
        spectral_centroid_,
        beat_position_,
        tempo_consistency_
    );
}

std::vector<uint8_t> BPMAudioProcessor::createStatusUpdate(float bpm, float confidence) {
    flatbuffers::FlatBufferBuilder builder;

    // Create status update
    auto status_offset = sparesparrow::bpm::CreateStatusUpdate(
        builder,
        bpm,
        confidence,
        sparesparrow::bpm::DetectionStatus_DETECTED,
        millis()
    );

    // Create message envelope
    auto envelope_offset = sparesparrow::bpm::CreateHeader(
        builder,
        sparesparrow::bpm::MessageType_STATUS_UPDATE,
        millis(),
        2, // message_id
        sparesparrow::bpm::CreateMessagePayload(builder, sparesparrow::bpm::Payload_StatusUpdate, status_offset.Union())
    );

    builder.Finish(envelope_offset);
    return std::vector<uint8_t>(builder.GetBufferPointer(), builder.GetBufferPointer() + builder.GetSize());
}

// BPMProtocolHandler Implementation
BPMProtocolHandler::BPMProtocolHandler()
    : next_message_id_(1)
    , audio_processor_(new BPMAudioProcessor())
{
}

BPMProtocolHandler::~BPMProtocolHandler() {
    delete audio_processor_;
}

std::vector<uint8_t> BPMProtocolHandler::processMessage(const std::vector<uint8_t>& message) {
    // Parse incoming FlatBuffers message
    auto verifier = flatbuffers::Verifier(message.data(), message.size());
    if (!sparesparrow::bpm::VerifyHeaderBuffer(verifier)) {
        // Invalid message - return error response
        return createErrorResponse("Invalid BPM message format");
    }

    auto header = sparesparrow::bpm::GetHeader(message.data());

    // Process based on message type
    switch (header->message_type()) {
        case sparesparrow::bpm::MessageType_BPM_REQUEST: {
            // Handle BPM request - return current BPM data
            return audio_processor_->createStatusUpdate(
                audio_processor_->getBPMAnalysis().bpm(),
                0.85f // confidence
            );
        }

        case sparesparrow::bpm::MessageType_CONFIG_UPDATE: {
            // Handle configuration update
            // In a real implementation, this would update audio processing parameters
            return createAckResponse(header->message_id(), "Configuration updated");
        }

        default:
            return createErrorResponse("Unsupported message type");
    }
}

void BPMProtocolHandler::sendBPMUpdate(float bpm, float confidence, uint64_t timestamp) {
    // In a real implementation, this would send the message via UART, BLE, WiFi, etc.
    auto message = audio_processor_->createStatusUpdate(bpm, confidence);
    // Send message to connected clients...
    Serial.println("BPM Update sent to clients");
}

void BPMProtocolHandler::sendStatusUpdate(sparesparrow::bpm::DetectionStatus status) {
    flatbuffers::FlatBufferBuilder builder;

    // Create status update
    auto status_offset = sparesparrow::bpm::CreateStatusUpdate(
        builder,
        audio_processor_->getBPMAnalysis().bpm(),
        0.85f, // confidence
        status,
        millis()
    );

    // Create message envelope
    auto envelope_offset = sparesparrow::bpm::CreateHeader(
        builder,
        sparesparrow::bpm::MessageType_STATUS_UPDATE,
        millis(),
        next_message_id_++,
        sparesparrow::bpm::CreateMessagePayload(builder, sparesparrow::bpm::Payload_StatusUpdate, status_offset.Union())
    );

    builder.Finish(envelope_offset);

    // Send to clients
    std::vector<uint8_t> message(builder.GetBufferPointer(), builder.GetBufferPointer() + builder.GetSize());
    // Send message...
    Serial.println("Status update sent to clients");
}

std::vector<uint8_t> BPMProtocolHandler::createErrorResponse(const std::string& error_msg) {
    flatbuffers::FlatBufferBuilder builder;

    // Create error message
    auto error_offset = sparesparrow::bpm::CreateErrorReport(
        builder,
        sparesparrow::bpm::ErrorSeverity_ERROR,
        sparesparrow::bpm::ErrorCode_INVALID_REQUEST,
        builder.CreateString(error_msg),
        millis()
    );

    // Create message envelope
    auto envelope_offset = sparesparrow::bpm::CreateHeader(
        builder,
        sparesparrow::bpm::MessageType_ERROR_REPORT,
        millis(),
        next_message_id_++,
        sparesparrow::bpm::CreateMessagePayload(builder, sparesparrow::bpm::Payload_ErrorReport, error_offset.Union())
    );

    builder.Finish(envelope_offset);
    return std::vector<uint8_t>(builder.GetBufferPointer(), builder.GetBufferPointer() + builder.GetSize());
}

std::vector<uint8_t> BPMProtocolHandler::createAckResponse(uint32_t request_id, const std::string& message) {
    flatbuffers::FlatBufferBuilder builder;

    // Create acknowledgment
    auto ack_offset = sparesparrow::bpm::CreateCommandAck(
        builder,
        builder.CreateString(std::to_string(request_id)),
        sparesparrow::bpm::CommandStatus_SUCCESS,
        builder.CreateString(message),
        0, // no response data
        millis()
    );

    // Create message envelope
    auto envelope_offset = sparesparrow::bpm::CreateHeader(
        builder,
        sparesparrow::bpm::MessageType_COMMAND_ACK,
        millis(),
        next_message_id_++,
        sparesparrow::bpm::CreateMessagePayload(builder, sparesparrow::bpm::Payload_CommandAck, ack_offset.Union())
    );

    builder.Finish(envelope_offset);
    return std::vector<uint8_t>(builder.GetBufferPointer(), builder.GetBufferPointer() + builder.GetSize());
}

} // namespace bpm
} // namespace nucleus

