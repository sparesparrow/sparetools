#include "schema_test_framework.h"
#include <iostream>
#include <chrono>
#include <vector>

// Test implementations using the framework

TEST_F(CrossPlatformTest, BPMSerialization) {
    testBPMSerialization();
}

TEST_F(CrossPlatformTest, GPIOCommand) {
    testGPIOCommand();
}

TEST(BasicSchemaTest, SchemaCreation) {
    flatbuffers::FlatBufferBuilder builder;

    // Test BPM request creation
    auto get_status = sparesparrow::bpm::CreateGetStatusRequest(builder);
    auto header = sparesparrow::bpm::CreateHeader(builder, 1);
    auto request = sparesparrow::bpm::CreateRequest(builder, header,
        sparesparrow::bpm::RequestType_GetStatus, get_status.Union());
    builder.Finish(request);

    // Verify the buffer
    flatbuffers::Verifier verifier(builder.GetBufferPointer(), builder.GetSize());
    ASSERT_TRUE(sparesparrow::bpm::VerifyRequestBuffer(verifier));
}

TEST(BasicSchemaTest, MCPMessage) {
    flatbuffers::FlatBufferBuilder builder;

    // Test MCP GPIO command
    auto gpio_cmd = sparesparrow::mcp::CreateGPIOCommand(builder,
        2, true, sparesparrow::mcp::GPIOMode_INPUT, 1234567890ULL);
    auto envelope = sparesparrow::mcp::CreateMCEnvelope(builder,
        sparesparrow::mcp::MCPMessage_GPIOCommand, gpio_cmd.Union());
    builder.Finish(envelope);

    // Verify the buffer
    flatbuffers::Verifier verifier(builder.GetBufferPointer(), builder.GetSize());
    ASSERT_TRUE(sparesparrow::mcp::VerifyMCEnvelopeBuffer(verifier));
}

TEST_F(PerformanceTest, BenchmarkOperations) {
    const int iterations = 1000;

    // Benchmark serialization
    benchmarkSerialization(iterations);

    // Create test data for deserialization benchmark
    std::vector<std::vector<uint8_t>> test_buffers;
    for (int i = 0; i < iterations; ++i) {
        builder_.Clear();
        auto bpm_update = sparetools::bpm::CreateBPMUpdate(builder_,
            test_bpm_ + i, test_confidence_, 0.8f,
            sparetools::bpm::DetectionStatus_DETECTING,
            test_timestamp_ + i);
        builder_.Finish(bpm_update);

        test_buffers.emplace_back(builder_.GetBufferPointer(),
                                builder_.GetBufferPointer() + builder_.GetSize());
    }

    // Benchmark deserialization
    benchmarkDeserialization(test_buffers);
}

TEST_F(FuzzTest, RandomDataParsing) {
    // Generate and test random data
    for (int i = 0; i < 100; ++i) {
        auto random_data = generateRandomData(64 + (rand() % 128));
        fuzzTestBPM(random_data.data(), random_data.size());
    }
}

// Integration tests combining multiple components
TEST(SchemaIntegrationTest, EndToEndWorkflow) {
    flatbuffers::FlatBufferBuilder builder;

    // 1. Create BPM update (simulating ESP32)
    auto bpm_update = sparetools::bpm::CreateBPMUpdate(builder,
        75.5f, 0.92f, 0.85f,
        sparetools::bpm::DetectionStatus_DETECTING,
        1234567890000ULL);
    builder.Finish(bpm_update);

    auto buffer = builder.GetBufferPointer();
    auto size = builder.GetSize();

    // 2. Verify message integrity
    flatbuffers::Verifier verifier(buffer, size);
    ASSERT_TRUE(sparetools::bpm::VerifyBPMUpdateBuffer(verifier));

    // 3. Parse message (simulating Android/MCP)
    auto parsed = sparetools::bpm::GetBPMUpdate(buffer);
    ASSERT_FLOAT_EQ(parsed->bpm(), 75.5f);
    ASSERT_FLOAT_EQ(parsed->confidence(), 0.92f);
    ASSERT_EQ(parsed->status(), sparetools::bpm::DetectionStatus_DETECTING);

    // 4. Create response (simulating server response)
    builder.Clear();
    auto response = sparetools::common::CreateResponse(builder,
        sparetools::common::Status_OK,
        builder.CreateString("BPM update processed successfully"),
        1234567890001ULL,
        42ULL);
    builder.Finish(response);

    // 5. Verify response
    flatbuffers::Verifier resp_verifier(builder.GetBufferPointer(), builder.GetSize());
    ASSERT_TRUE(sparetools::common::VerifyResponseBuffer(resp_verifier));

    auto parsed_response = sparetools::common::GetResponse(builder.GetBufferPointer());
    ASSERT_EQ(parsed_response->status(), sparetools::common::Status_OK);
}

TEST(SchemaIntegrationTest, ErrorHandling) {
    flatbuffers::FlatBufferBuilder builder;

    // Test invalid data handling
    std::vector<uint8_t> invalid_data = {0xFF, 0xFF, 0xFF, 0xFF};
    flatbuffers::Verifier verifier(invalid_data.data(), invalid_data.size());

    // Should fail verification safely
    ASSERT_FALSE(sparetools::bpm::VerifyBPMUpdateBuffer(verifier));
    ASSERT_FALSE(sparetools::common::VerifyResponseBuffer(verifier));
}

int main(int argc, char **argv) {
    std::cout << "SpareTools FlatBuffers Schema Compatibility Tests" << std::endl;
    std::cout << "=================================================" << std::endl;

    // Initialize random seed for fuzz tests
    srand(static_cast<unsigned int>(time(nullptr)));

    ::testing::InitGoogleTest(&argc, argv);

    auto start_time = std::chrono::high_resolution_clock::now();
    int result = RUN_ALL_TESTS();
    auto end_time = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);

    std::cout << "\n=================================================" << std::endl;
    std::cout << "Test execution completed in " << duration.count() << " ms" << std::endl;

    if (result == 0) {
        std::cout << "✅ All schema compatibility tests passed!" << std::endl;
    } else {
        std::cout << "❌ Some tests failed. Check output above." << std::endl;
    }

    return result;
}