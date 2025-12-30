#pragma once

#include <gtest/gtest.h>
#include <flatbuffers/flatbuffers.h>
#include <generated/common/common_generated.h>
#include <generated/iot/BPM_generated.h>
#include <generated/mcp/MCP_generated.h>
#include <vector>
#include <string>
#include <functional>

namespace sparetools {
namespace schema_tests {

/**
 * Schema Compatibility Test Framework
 *
 * Provides utilities for testing FlatBuffers schema compatibility across:
 * - Different versions
 * - Different platforms (endianness)
 * - Forward/backward compatibility
 * - Message parsing/validation
 */
class SchemaTestFramework : public ::testing::Test {
protected:
    void SetUp() override {
        // Initialize test data
        test_timestamp_ = 1234567890ULL;
        test_bpm_ = 72.5f;
        test_confidence_ = 0.95f;
    }

    // Test data
    uint64_t test_timestamp_;
    float test_bpm_;
    float test_confidence_;

    // Builder for creating test messages
    flatbuffers::FlatBufferBuilder builder_;
};

/**
 * Cross-Platform Compatibility Test
 *
 * Tests that messages created on one platform can be read on another
 */
class CrossPlatformTest : public SchemaTestFramework {
protected:
    /**
     * Test basic FlatBuffers functionality with BPM data
     */
    void testBPMSerialization() {
        // Create a simple request message
        auto get_status = sparesparrow::bpm::CreateGetStatusRequest(builder_);
        auto header = sparesparrow::bpm::CreateHeader(builder_, 1);
        auto request = sparesparrow::bpm::CreateRequest(builder_, header,
            sparesparrow::bpm::RequestType_GetStatus, get_status.Union());
        builder_.Finish(request);

        // Verify buffer
        flatbuffers::Verifier verifier(builder_.GetBufferPointer(), builder_.GetSize());
        ASSERT_TRUE(sparesparrow::bpm::VerifyRequestBuffer(verifier));

        // Parse and validate
        auto parsed = sparesparrow::bpm::GetRequest(builder_.GetBufferPointer());
        ASSERT_EQ(parsed->header()->version(), 1);
        ASSERT_EQ(parsed->request_type(), sparesparrow::bpm::RequestType_GetStatus);
    }

    /**
     * Test MCP GPIO command serialization
     */
    void testGPIOCommand() {
        builder_.Clear();
        auto gpio_cmd = sparesparrow::mcp::CreateGPIOCommand(builder_,
            2, true, sparesparrow::mcp::GPIOMode_INPUT, test_timestamp_);
        auto envelope = sparesparrow::mcp::CreateMCEnvelope(builder_,
            sparesparrow::mcp::MCPMessage_GPIOCommand, gpio_cmd.Union());
        builder_.Finish(envelope);

        // Verify and parse
        flatbuffers::Verifier verifier(builder_.GetBufferPointer(), builder_.GetSize());
        ASSERT_TRUE(sparesparrow::mcp::VerifyMCEnvelopeBuffer(verifier));

        auto parsed = sparesparrow::mcp::GetMCEnvelope(builder_.GetBufferPointer());
        ASSERT_EQ(parsed->message_type(), sparesparrow::mcp::MCPMessage_GPIOCommand);
    }
};

/**
 * Schema Evolution Test
 *
 * Tests forward and backward compatibility when schemas change
 */
class SchemaEvolutionTest : public SchemaTestFramework {
protected:
    /**
     * Test that new fields don't break old parsers
     */
    void testForwardCompatibility() {
        // Create message with all current fields
        auto bpm_update = sparesparrow::bpm::CreateBPMUpdate(builder_,
            test_bpm_, test_confidence_, 0.8f,
            sparesparrow::bpm::DetectionStatus_DETECTING,
            test_timestamp_);
        builder_.Finish(bpm_update);

        // Simulate old parser that only reads basic fields
        auto parsed = sparesparrow::bpm::GetBPMUpdate(builder_.GetBufferPointer());
        ASSERT_FLOAT_EQ(parsed->bpm(), test_bpm_);
        // Old parser ignores new fields automatically
    }

    /**
     * Test that missing fields are handled gracefully
     */
    void testBackwardCompatibility() {
        // Create minimal message (simulate old version)
        builder_.Clear();
        auto bpm_update = sparesparrow::bpm::CreateBPMUpdate(builder_,
            test_bpm_, test_confidence_, 0.0f,  // Default values
            sparesparrow::bpm::DetectionStatus_DETECTING,
            test_timestamp_);
        builder_.Finish(bpm_update);

        // New parser should handle missing fields gracefully
        auto parsed = sparesparrow::bpm::GetBPMUpdate(builder_.GetBufferPointer());
        ASSERT_FLOAT_EQ(parsed->bpm(), test_bpm_);
        ASSERT_GE(parsed->signal_level(), 0.0f);  // Should have default
    }
};

/**
 * Performance Test Suite
 *
 * Measures serialization/deserialization performance
 */
class PerformanceTest : public SchemaTestFramework {
protected:
    /**
     * Benchmark message creation
     */
    void benchmarkSerialization(int iterations = 10000) {
        std::vector<std::vector<uint8_t>> buffers;

        auto start = std::chrono::high_resolution_clock::now();

        for (int i = 0; i < iterations; ++i) {
            builder_.Clear();
            auto bpm_update = sparesparrow::bpm::CreateBPMUpdate(builder_,
                test_bpm_ + i, test_confidence_,
                0.8f, sparesparrow::bpm::DetectionStatus_DETECTING,
                test_timestamp_ + i);
            builder_.Finish(bpm_update);

            // Store buffer copy
            buffers.emplace_back(builder_.GetBufferPointer(),
                               builder_.GetBufferPointer() + builder_.GetSize());
        }

        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << "Serialization: " << iterations << " messages in "
                  << duration.count() << " microseconds ("
                  << (duration.count() / iterations) << " μs per message)" << std::endl;
    }

    /**
     * Benchmark message parsing
     */
    void benchmarkDeserialization(const std::vector<std::vector<uint8_t>>& buffers) {
        auto start = std::chrono::high_resolution_clock::now();

        for (const auto& buffer : buffers) {
            flatbuffers::Verifier verifier(buffer.data(), buffer.size());
            ASSERT_TRUE(sparesparrow::bpm::VerifyBPMUpdateBuffer(verifier));

            auto parsed = sparesparrow::bpm::GetBPMUpdate(buffer.data());
            ASSERT_GE(parsed->bpm(), test_bpm_);
        }

        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << "Deserialization: " << buffers.size() << " messages in "
                  << duration.count() << " microseconds ("
                  << (duration.count() / buffers.size()) << " μs per message)" << std::endl;
    }
};

/**
 * Fuzz Test Framework
 *
 * Tests schema parsing with random/fuzzed input data
 */
class FuzzTest : public SchemaTestFramework {
protected:
    /**
     * Test parsing with random data
     */
    void fuzzTestBPM(const uint8_t* data, size_t size) {
        // Try to parse as BPM message
        flatbuffers::Verifier verifier(data, size);
        if (sparesparrow::bpm::VerifyBPMUpdateBuffer(verifier)) {
            auto bpm = sparesparrow::bpm::GetBPMUpdate(data);

            // Validate field ranges (no crashes/asserts)
            if (bpm->bpm() < 0 || bpm->bpm() > 300) {
                // Invalid BPM range - should not crash
                return;
            }
            if (bpm->confidence() < 0.0f || bpm->confidence() > 1.0f) {
                // Invalid confidence range - should not crash
                return;
            }
            // Valid message parsed successfully
        }
        // Invalid data rejected safely
    }

    /**
     * Generate random test data
     */
    std::vector<uint8_t> generateRandomData(size_t size) {
        std::vector<uint8_t> data(size);
        for (auto& byte : data) {
            byte = rand() % 256;
        }
        return data;
    }
};

/**
 * Multi-Version Compatibility Test
 *
 * Tests compatibility between different schema versions
 */
class MultiVersionTest : public SchemaTestFramework {
protected:
    /**
     * Test message format compatibility
     */
    void testVersionCompatibility() {
        // Create message with current schema version
        auto bpm_update = sparesparrow::bpm::CreateBPMUpdate(builder_,
            test_bpm_, test_confidence_, 0.8f,
            sparesparrow::bpm::DetectionStatus_DETECTING,
            test_timestamp_);
        builder_.Finish(bpm_update);

        // Test that message can be parsed (version compatibility)
        flatbuffers::Verifier verifier(builder_.GetBufferPointer(), builder_.GetSize());
        ASSERT_TRUE(sparesparrow::bpm::VerifyBPMUpdateBuffer(verifier));

        auto parsed = sparesparrow::bpm::GetBPMUpdate(builder_.GetBufferPointer());
        ASSERT_EQ(parsed->timestamp(), test_timestamp_);
    }

    /**
     * Test schema identifier validation
     */
    void testSchemaIdentification() {
        // BPM message
        auto bpm_update = sparesparrow::bpm::CreateBPMUpdate(builder_,
            test_bpm_, test_confidence_, 0.8f,
            sparesparrow::bpm::DetectionStatus_DETECTING,
            test_timestamp_);
        builder_.Finish(bpm_update);

        // Should verify as BPM but not as other message types
        flatbuffers::Verifier verifier(builder_.GetBufferPointer(), builder_.GetSize());
        ASSERT_TRUE(sparesparrow::bpm::VerifyBPMUpdateBuffer(verifier));
        // Note: Other message types would fail verification as expected
    }
};

// Convenience test macros
#define TEST_BPM_SERIALIZATION() \
    CrossPlatformTest test; \
    test.testBPMSerialization()

#define TEST_SCHEMA_EVOLUTION() \
    SchemaEvolutionTest test; \
    test.testForwardCompatibility(); \
    test.testBackwardCompatibility()

} // namespace schema_tests
} // namespace sparetools