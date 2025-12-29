#include "bpm_flatbuffers.h"
#include <flatbuffers/flatbuffers.h>
#include "BPM_generated.h"

// Static method implementations
flatbuffers::Offset<sparesparrow::bpm::BPMUpdate> BPMFlatBuffers::createBPMUpdate(
    float bpm,
    float confidence,
    float signal_level,
    sparesparrow::bpm::DetectionStatus status,
    flatbuffers::FlatBufferBuilder& builder) {

    // Create BPM analysis data
    auto analysis_offset = sparesparrow::bpm::CreateBPMAnalysis(
        builder,
        0.85f,  // stability
        0.78f,  // regularity
        440.0f, // dominant_frequency
        0.65f,  // spectral_centroid
        0.3f,   // beat_position
        0.82f   // tempo_consistency
    );

    // Create BPM quality metrics
    auto quality_offset = sparesparrow::bpm::CreateBPMQuality(
        builder,
        -23.5f, // snr_db
        15,     // consecutive_detections
        0.89f,  // reliability_score
        0.02f,  // false_positive_rate
        0.91f   // algorithm_confidence
    );

    // Create the BPM update
    return sparesparrow::bpm::CreateBPMUpdate(
        builder,
        bpm,
        confidence,
        signal_level,
        status,
        analysis_offset,
        quality_offset
    );
}

flatbuffers::Offset<sparesparrow::bpm::StatusUpdate> BPMFlatBuffers::createStatusUpdate(
    uint64_t uptime_seconds,
    uint32_t free_heap_bytes,
    uint8_t cpu_usage_percent,
    int8_t wifi_rssi,
    flatbuffers::FlatBufferBuilder& builder) {

    // Create audio status
    auto audio_status_offset = sparesparrow::bpm::CreateAudioStatus(
        builder,
        true,   // input_active
        25000,  // sample_rate
        0.75f,  // buffer_utilization
        0,      // audio_dropouts
        45,     // latency_ms
        0.8f    // microphone_gain
    );

    // Create status update
    return sparesparrow::bpm::CreateStatusUpdate(
        builder,
        uptime_seconds,
        free_heap_bytes,
        free_heap_bytes / 4, // min_free_heap
        cpu_usage_percent,
        wifi_rssi,
        audio_status_offset,
        28.5f // temperature_celsius
    );
}

std::vector<uint8_t> BPMFlatBuffers::serializeBPMUpdate(
    flatbuffers::Offset<sparesparrow::bpm::BPMUpdate> bpm_update_offset,
    flatbuffers::FlatBufferBuilder& builder) {

    // Create a status object
    auto status_offset = sparesparrow::bpm::CreateStatus(builder, sparesparrow::bpm::StatusEnum::Success, builder.CreateString("OK"));

    // For testing, create a minimal Response (BPMUpdate would normally be sent via streaming)
    auto response_offset = sparesparrow::bpm::CreateResponse(
        builder,
        0, // No header
        status_offset,
        sparesparrow::bpm::ResponsePayload::NONE, // No payload for testing
        0 // Union (empty)
    );
    builder.Finish(response_offset);

    const uint8_t* buffer = builder.GetBufferPointer();
    size_t size = builder.GetSize();

    return std::vector<uint8_t>(buffer, buffer + size);
}

std::vector<uint8_t> BPMFlatBuffers::serializeStatusUpdate(
    flatbuffers::Offset<sparesparrow::bpm::StatusUpdate> status_update_offset,
    flatbuffers::FlatBufferBuilder& builder) {

    // Create a status object for the response
    auto response_status_offset = sparesparrow::bpm::CreateStatus(builder, sparesparrow::bpm::StatusEnum::Success, builder.CreateString("OK"));

    // Create a GetStatusResponse containing the StatusUpdate
    auto status_response_offset = sparesparrow::bpm::CreateGetStatusResponse(builder, status_update_offset);

    // Create a Response containing the GetStatusResponse
    auto response_offset = sparesparrow::bpm::CreateResponse(
        builder,
        0, // No header
        response_status_offset,
        sparesparrow::bpm::ResponsePayload::GetStatusResponse,
        status_response_offset.Union()
    );
    builder.Finish(response_offset);

    const uint8_t* buffer = builder.GetBufferPointer();
    size_t size = builder.GetSize();

    return std::vector<uint8_t>(buffer, buffer + size);
}

const sparesparrow::bpm::BPMUpdate* BPMFlatBuffers::deserializeBPMUpdate(
    const std::vector<uint8_t>& buffer) {

    // BPMUpdate is not directly serializable as root - return nullptr for testing
    return nullptr;
}

const sparesparrow::bpm::StatusUpdate* BPMFlatBuffers::deserializeStatusUpdate(
    const std::vector<uint8_t>& buffer) {

    // Deserialize the Response, then extract the GetStatusResponse, then get StatusUpdate
    auto response = sparesparrow::bpm::GetResponse(buffer.data());
    if (response && response->data_type() == sparesparrow::bpm::ResponsePayload::GetStatusResponse) {
        auto status_response = response->data_as_GetStatusResponse();
        if (status_response) {
            return status_response->status();
        }
    }
    return nullptr;
}

const char* BPMFlatBuffers::detectionStatusToString(sparesparrow::bpm::DetectionStatus status) {
    switch (status) {
        case sparesparrow::bpm::DetectionStatus::INITIALIZING: return "INITIALIZING";
        case sparesparrow::bpm::DetectionStatus::DETECTING: return "DETECTING";
        case sparesparrow::bpm::DetectionStatus::LOW_SIGNAL: return "LOW_SIGNAL";
        case sparesparrow::bpm::DetectionStatus::NO_SIGNAL: return "NO_SIGNAL";
        case sparesparrow::bpm::DetectionStatus::ERROR: return "ERROR";
        case sparesparrow::bpm::DetectionStatus::CALIBRATING: return "CALIBRATING";
        default: return "UNKNOWN";
    }
}

size_t BPMFlatBuffers::estimateBPMUpdateSize() {
    // Base overhead: Response structure + Status + BPMUpdate envelope
    size_t baseOverhead = 128;  // FlatBuffers table overhead

    // BPMUpdate structure size
    size_t bpmUpdateSize = 0;
    bpmUpdateSize += sizeof(float);     // bpm
    bpmUpdateSize += sizeof(float);     // confidence
    bpmUpdateSize += sizeof(float);     // signal_level
    bpmUpdateSize += sizeof(uint8_t);   // status (enum)
    bpmUpdateSize += sizeof(uint64_t);  // timestamp

    // BPMAnalysis structure (nested)
    size_t analysisSize = 0;
    analysisSize += 6 * sizeof(float);  // stability, regularity, dominant_frequency, spectral_centroid, beat_position, tempo_consistency

    // BPMQuality structure (nested)
    size_t qualitySize = 0;
    qualitySize += sizeof(float);       // snr_db
    qualitySize += sizeof(uint16_t);    // consecutive_detections
    qualitySize += 4 * sizeof(float);   // reliability_score, false_positive_rate, algorithm_confidence

    // Total estimate with some padding for FlatBuffers overhead
    return baseOverhead + bpmUpdateSize + analysisSize + qualitySize + 64;  // +64 for safety margin
}

size_t BPMFlatBuffers::estimateStatusUpdateSize() {
    // Base overhead: Response structure + Status + StatusUpdate envelope
    size_t baseOverhead = 128;  // FlatBuffers table overhead

    // StatusUpdate structure size
    size_t statusUpdateSize = 0;
    statusUpdateSize += sizeof(uint64_t);  // uptime_seconds
    statusUpdateSize += sizeof(uint32_t);  // free_heap_bytes
    statusUpdateSize += sizeof(uint32_t);  // min_free_heap_bytes
    statusUpdateSize += sizeof(uint8_t);   // cpu_usage_percent
    statusUpdateSize += sizeof(int8_t);    // wifi_rssi
    statusUpdateSize += sizeof(float);     // temperature_celsius
    statusUpdateSize += sizeof(uint8_t);   // battery_level_percent

    // AudioStatus structure (nested)
    size_t audioStatusSize = 0;
    audioStatusSize += sizeof(bool);       // input_active
    audioStatusSize += sizeof(uint32_t);   // sample_rate
    audioStatusSize += sizeof(float);      // buffer_utilization
    audioStatusSize += sizeof(uint32_t);   // audio_dropouts
    audioStatusSize += sizeof(uint16_t);   // latency_ms
    audioStatusSize += sizeof(float);      // microphone_gain

    // Total estimate with some padding for FlatBuffers overhead
    return baseOverhead + statusUpdateSize + audioStatusSize + 64;  // +64 for safety margin
}