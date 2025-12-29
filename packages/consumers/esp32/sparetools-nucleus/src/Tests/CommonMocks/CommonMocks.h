//
// CommonMocks.h
// Common mock objects for NucleusESP32 unit tests
// Following oms-dev/Src/Tests/CommonMocks/ pattern
//

#pragma once

#include "gmock/gmock.h"
#include "../../test/mock_arduino.h"
#include "../../test/mock_nfc_reader.h"

namespace NucleusESP32 {
namespace Mock {

// Mock hardware interfaces
class MockHardware {
public:
    MOCK_METHOD(void, pinMode, (int pin, int mode), ());
    MOCK_METHOD(void, digitalWrite, (int pin, int value), ());
    MOCK_METHOD(int, digitalRead, (int pin), ());
    MOCK_METHOD(int, analogRead, (int pin), ());
    MOCK_METHOD(unsigned long, millis, (), ());
    MOCK_METHOD(unsigned long, micros, (), ());
    MOCK_METHOD(void, delay, (unsigned long ms), ());
};

// Mock SPI interface
class MockSPI {
public:
    MOCK_METHOD(void, begin, (), ());
    MOCK_METHOD(void, beginTransaction, (int settings), ());
    MOCK_METHOD(void, endTransaction, (), ());
    MOCK_METHOD(uint8_t, transfer, (uint8_t data), ());
    MOCK_METHOD(void, end, (), ());
};

// Mock NFC reader
class MockNFCReader {
public:
    MOCK_METHOD(bool, init, (), ());
    MOCK_METHOD(bool, isCardPresent, (), ());
    MOCK_METHOD(bool, readCard, (uint8_t* uid, uint8_t* uidLength), ());
    MOCK_METHOD(void, halt, (), ());
};

// Mock RF transceiver
class MockRFTransceiver {
public:
    MOCK_METHOD(bool, init, (), ());
    MOCK_METHOD(bool, sendData, (const uint8_t* data, size_t length), ());
    MOCK_METHOD(bool, receiveData, (uint8_t* buffer, size_t* length), ());
    MOCK_METHOD(bool, setFrequency, (float frequency), ());
};

// Mock IR transceiver
class MockIRTransceiver {
public:
    MOCK_METHOD(bool, init, (), ());
    MOCK_METHOD(bool, sendCode, (uint32_t code, int protocol), ());
    MOCK_METHOD(bool, receiveCode, (uint32_t* code, int* protocol), ());
};

// Mock SD card
class MockSDCard {
public:
    MOCK_METHOD(bool, begin, (), ());
    MOCK_METHOD(bool, exists, (const char* path), ());
    MOCK_METHOD(bool, mkdir, (const char* path), ());
    MOCK_METHOD(bool, remove, (const char* path), ());
};

} // namespace Mock
} // namespace NucleusESP32
