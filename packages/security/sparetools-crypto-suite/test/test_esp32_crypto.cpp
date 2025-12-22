/**
 * @file test_esp32_crypto.cpp
 * @brief Unit tests for ESP32 cryptographic functions
 */

#include <gtest/gtest.h>
#include "crypto/esp32_crypto.h"

// Test fixture for crypto tests
class ESP32CryptoTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Initialize crypto library with mbedTLS backend
        esp32_crypto_result_t result = esp32_crypto_init(ESP32_CRYPTO_BACKEND_MBEDTLS);
        ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);
    }

    void TearDown() override {
        esp32_crypto_deinit();
    }
};

// Test basic initialization
TEST_F(ESP32CryptoTest, Initialization) {
    // Check that backend is correctly set
    esp32_crypto_backend_t backend = esp32_crypto_get_backend();
    EXPECT_EQ(backend, ESP32_CRYPTO_BACKEND_MBEDTLS);

    // Check hardware acceleration availability
    bool hw_accel = esp32_crypto_hw_acceleration_available();
    // Note: This will depend on the actual hardware/target
    (void)hw_accel; // Suppress unused variable warning
}

// Test AES encryption/decryption
TEST_F(ESP32CryptoTest, AES_EncryptionDecryption) {
    const uint8_t key[32] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F
    };
    const uint8_t iv[16] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    };
    const uint8_t plaintext[16] = {
        0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48,
        0x49, 0x4A, 0x4B, 0x4C, 0x4D, 0x4E, 0x4F, 0x50
    };

    uint8_t ciphertext[16];
    uint8_t decrypted[16];
    size_t output_len;

    // Test encryption
    esp32_aes_context_t* enc_ctx = nullptr;
    esp32_crypto_result_t result = esp32_aes_init(&enc_ctx, key, ESP32_CRYPTO_AES_256,
                                                 ESP32_CRYPTO_AES_MODE_CBC, true);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);
    ASSERT_NE(enc_ctx, nullptr);

    result = esp32_aes_set_iv(enc_ctx, iv, sizeof(iv));
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);

    result = esp32_aes_process(enc_ctx, plaintext, sizeof(plaintext), ciphertext, &output_len);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);
    ASSERT_EQ(output_len, sizeof(plaintext));

    esp32_aes_free(enc_ctx);

    // Test decryption
    esp32_aes_context_t* dec_ctx = nullptr;
    result = esp32_aes_init(&dec_ctx, key, ESP32_CRYPTO_AES_256,
                           ESP32_CRYPTO_AES_MODE_CBC, false);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);
    ASSERT_NE(dec_ctx, nullptr);

    result = esp32_aes_set_iv(dec_ctx, iv, sizeof(iv));
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);

    result = esp32_aes_process(dec_ctx, ciphertext, sizeof(ciphertext), decrypted, &output_len);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);
    ASSERT_EQ(output_len, sizeof(plaintext));

    esp32_aes_free(dec_ctx);

    // Verify decryption matches original plaintext
    ASSERT_EQ(memcmp(plaintext, decrypted, sizeof(plaintext)), 0);
}

// Test SHA-256 hashing
TEST_F(ESP32CryptoTest, SHA256_Hashing) {
    const uint8_t test_data[] = "Hello, World!";
    const uint8_t expected_hash[32] = {
        0xD0, 0x19, 0x2F, 0x9C, 0x6D, 0xF8, 0x9B, 0x23,
        0xF8, 0x8C, 0x6E, 0xF8, 0x29, 0x8C, 0x1F, 0x57,
        0x5C, 0x4A, 0x2C, 0x8B, 0x5E, 0x8D, 0x8B, 0x2C,
        0x2D, 0x55, 0x9F, 0x5F, 0x9F, 0x0E, 0x7A, 0xCB
    };

    uint8_t hash[32];
    size_t hash_len;

    esp32_crypto_result_t result = esp32_sha_compute(ESP32_CRYPTO_SHA_256,
                                                    test_data, strlen((const char*)test_data),
                                                    hash, &hash_len);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);
    ASSERT_EQ(hash_len, 32);

    // Verify hash matches expected value
    ASSERT_EQ(memcmp(hash, expected_hash, 32), 0);
}

// Test RNG generation
TEST_F(ESP32CryptoTest, RNG_Generation) {
    uint8_t random_data[64];
    esp32_crypto_result_t result = esp32_rng_fill(random_data, sizeof(random_data));
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);

    // Basic statistical test - check that not all bytes are the same
    bool all_same = true;
    for (size_t i = 1; i < sizeof(random_data); ++i) {
        if (random_data[i] != random_data[0]) {
            all_same = false;
            break;
        }
    }
    ASSERT_FALSE(all_same) << "RNG generated all identical bytes - unlikely for good RNG";
}

// Test ECC key generation
TEST_F(ESP32CryptoTest, ECC_KeyGeneration) {
    esp32_ecc_context_t* ctx = nullptr;
    esp32_crypto_result_t result = esp32_ecc_init(&ctx, ESP32_CRYPTO_ECC_P256);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);
    ASSERT_NE(ctx, nullptr);

    uint8_t private_key[32];
    uint8_t public_key[64];
    size_t priv_len, pub_len;

    result = esp32_ecc_generate_keypair(ctx, private_key, &priv_len, public_key, &pub_len);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);
    ASSERT_EQ(priv_len, 32); // P-256 private key size
    ASSERT_EQ(pub_len, 64);  // P-256 public key size (uncompressed)

    // Verify keys are not all zeros
    bool priv_zero = true, pub_zero = true;
    for (size_t i = 0; i < priv_len; ++i) {
        if (private_key[i] != 0) {
            priv_zero = false;
            break;
        }
    }
    for (size_t i = 0; i < pub_len; ++i) {
        if (public_key[i] != 0) {
            pub_zero = false;
            break;
        }
    }
    ASSERT_FALSE(priv_zero) << "Private key is all zeros";
    ASSERT_FALSE(pub_zero) << "Public key is all zeros";

    esp32_ecc_free(ctx);
}

// Test ECC sign and verify
TEST_F(ESP32CryptoTest, ECC_SignVerify) {
    esp32_ecc_context_t* ctx = nullptr;
    esp32_crypto_result_t result = esp32_ecc_init(&ctx, ESP32_CRYPTO_ECC_P256);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);

    // Generate key pair
    uint8_t private_key[32];
    uint8_t public_key[64];
    size_t priv_len, pub_len;
    result = esp32_ecc_generate_keypair(ctx, private_key, &priv_len, public_key, &pub_len);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);

    // Test data to sign
    const uint8_t test_data[] = "Test message for signing";
    const size_t data_len = strlen((const char*)test_data);

    // Sign the data
    uint8_t signature[64];
    size_t sig_len;
    result = esp32_ecc_sign(ctx, private_key, priv_len, test_data, data_len, signature, &sig_len);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);

    // Verify the signature
    result = esp32_ecc_verify(ctx, public_key, pub_len, test_data, data_len, signature, sig_len);
    ASSERT_EQ(result, ESP32_CRYPTO_SUCCESS);

    // Test with modified data (should fail)
    uint8_t modified_data[] = "Test message for signing - modified";
    result = esp32_ecc_verify(ctx, public_key, pub_len, modified_data,
                             strlen((const char*)modified_data), signature, sig_len);
    ASSERT_EQ(result, ESP32_CRYPTO_AUTH_FAILED);

    esp32_ecc_free(ctx);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}