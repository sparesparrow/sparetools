#ifndef BPM_FLATBUFFERS_H
#define BPM_FLATBUFFERS_H

// Platform-specific includes
#ifdef ARDUINO
    #include <Arduino.h>
#else
    // Standard C++ headers for non-Arduino environments (e.g., IDE analysis)
    #include <cstdint>
    #include <cstddef>
#endif

// Standard C++ headers (available in both Arduino and standard C++)
#include <vector>

#include <flatbuffers/flatbuffers.h>
#include "BPM_generated.h"

/**
 * BPM FlatBuffers Integration Header
 *
 * This header provides utility functions for serializing BPM detector data
 * using FlatBuffers for efficient binary communication.
 */

class BPMFlatBuffers {
public:
    /**
     * Create a BPM update message
     * @param bpm Detected BPM value
     * @param confidence Detection confidence (0.0-1.0)
     * @param signal_level Normalized signal strength (0.0-1.0)
     * @param status Detection status
     * @param builder FlatBuffers builder instance
     * @return Offset to the created message
     */
    static flatbuffers::Offset<sparesparrow::bpm::BPMUpdate> createBPMUpdate(
        float bpm,
        float confidence,
        float signal_level,
        sparesparrow::bpm::DetectionStatus status,
        flatbuffers::FlatBufferBuilder& builder);

    /**
     * Create a status update message
     * @param uptime_seconds Device uptime
     * @param free_heap_bytes Available heap memory
     * @param cpu_usage_percent CPU usage percentage
     * @param wifi_rssi WiFi signal strength
     * @param builder FlatBuffers builder instance
     * @return Offset to the created message
     */
    static flatbuffers::Offset<sparesparrow::bpm::StatusUpdate> createStatusUpdate(
        uint64_t uptime_seconds,
        uint32_t free_heap_bytes,
        uint8_t cpu_usage_percent,
        int8_t wifi_rssi,
        flatbuffers::FlatBufferBuilder& builder);

    /**
     * Serialize a BPM update to binary buffer
     * @param bpm_update_offset BPM update offset
     * @param builder FlatBuffers builder instance
     * @return Serialized binary data
     */
    static std::vector<uint8_t> serializeBPMUpdate(
        flatbuffers::Offset<sparesparrow::bpm::BPMUpdate> bpm_update_offset,
        flatbuffers::FlatBufferBuilder& builder);

    /**
     * Serialize a status update to binary buffer
     * @param status_update_offset Status update offset
     * @param builder FlatBuffers builder instance
     * @return Serialized binary data
     */
    static std::vector<uint8_t> serializeStatusUpdate(
        flatbuffers::Offset<sparesparrow::bpm::StatusUpdate> status_update_offset,
        flatbuffers::FlatBufferBuilder& builder);

    /**
     * Deserialize a BPM update from binary buffer
     * @param buffer Binary buffer containing serialized BPM update
     * @return Pointer to deserialized BPM update
     */
    static const sparesparrow::bpm::BPMUpdate* deserializeBPMUpdate(
        const std::vector<uint8_t>& buffer);

    /**
     * Deserialize a status update from binary buffer
     * @param buffer Binary buffer containing serialized status update
     * @return Pointer to deserialized status update
     */
    static const sparesparrow::bpm::StatusUpdate* deserializeStatusUpdate(
        const std::vector<uint8_t>& buffer);

    /**
     * Get detection status as string for debugging
     * @param status Detection status enum
     * @return Human-readable string
     */
    static const char* detectionStatusToString(sparesparrow::bpm::DetectionStatus status);

    /**
     * Calculate required buffer size for BPM update message
     * Useful for pre-allocating buffers in memory-constrained environments
     * @return Estimated buffer size in bytes
     */
    static size_t estimateBPMUpdateSize();

    /**
     * Calculate required buffer size for status update message
     * Useful for pre-allocating buffers in memory-constrained environments
     * @return Estimated buffer size in bytes
     */
    static size_t estimateStatusUpdateSize();
};

#endif // BPM_FLATBUFFERS_H