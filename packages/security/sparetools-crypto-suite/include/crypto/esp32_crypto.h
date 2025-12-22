#ifndef ESP32_CRYPTO_H
#define ESP32_CRYPTO_H

/**
 * @file esp32_crypto.h
 * @brief ESP32-specific cryptographic API with hardware acceleration support
 *
 * This header provides a unified cryptographic interface for ESP32 devices,
 * supporting multiple backends (mbedTLS, WolfSSL, OpenSSL) with hardware
 * acceleration when available.
 */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Cryptographic backend types
 */
typedef enum {
    ESP32_CRYPTO_BACKEND_MBEDTLS,    ///< mbedTLS backend
    ESP32_CRYPTO_BACKEND_WOLFSSL,    ///< WolfSSL backend
    ESP32_CRYPTO_BACKEND_OPENSSL,    ///< OpenSSL backend
} esp32_crypto_backend_t;

/**
 * @brief AES key sizes
 */
typedef enum {
    ESP32_CRYPTO_AES_128 = 16,       ///< 128-bit AES key
    ESP32_CRYPTO_AES_192 = 24,       ///< 192-bit AES key
    ESP32_CRYPTO_AES_256 = 32,       ///< 256-bit AES key
} esp32_crypto_aes_key_size_t;

/**
 * @brief AES operation modes
 */
typedef enum {
    ESP32_CRYPTO_AES_MODE_ECB,       ///< Electronic Code Book mode
    ESP32_CRYPTO_AES_MODE_CBC,       ///< Cipher Block Chaining mode
    ESP32_CRYPTO_AES_MODE_CTR,       ///< Counter mode
    ESP32_CRYPTO_AES_MODE_GCM,       ///< Galois/Counter Mode (authenticated encryption)
} esp32_crypto_aes_mode_t;

/**
 * @brief SHA hash algorithms
 */
typedef enum {
    ESP32_CRYPTO_SHA_256 = 256,      ///< SHA-256
    ESP32_CRYPTO_SHA_384 = 384,      ///< SHA-384
    ESP32_CRYPTO_SHA_512 = 512,      ///< SHA-512
} esp32_crypto_sha_type_t;

/**
 * @brief ECC curve types
 */
typedef enum {
    ESP32_CRYPTO_ECC_P256,           ///< NIST P-256 curve
    ESP32_CRYPTO_ECC_P384,           ///< NIST P-384 curve
    ESP32_CRYPTO_ECC_P521,           ///< NIST P-521 curve
} esp32_crypto_ecc_curve_t;

/**
 * @brief Crypto operation result codes
 */
typedef enum {
    ESP32_CRYPTO_SUCCESS = 0,        ///< Operation successful
    ESP32_CRYPTO_ERROR,              ///< Generic error
    ESP32_CRYPTO_INVALID_PARAM,      ///< Invalid parameter
    ESP32_CRYPTO_NOT_SUPPORTED,      ///< Operation not supported
    ESP32_CRYPTO_HW_ERROR,           ///< Hardware acceleration error
    ESP32_CRYPTO_AUTH_FAILED,        ///< Authentication failed
    ESP32_CRYPTO_BUFFER_TOO_SMALL,   ///< Output buffer too small
} esp32_crypto_result_t;

/**
 * @brief AES context structure
 */
typedef struct esp32_aes_context esp32_aes_context_t;

/**
 * @brief SHA context structure
 */
typedef struct esp32_sha_context esp32_sha_context_t;

/**
 * @brief ECC context structure
 */
typedef struct esp32_ecc_context esp32_ecc_context_t;

/**
 * @brief RNG context structure
 */
typedef struct esp32_rng_context esp32_rng_context_t;

/**
 * @brief Initialize the ESP32 crypto library
 *
 * This function must be called before using any crypto operations.
 * It detects available hardware acceleration and initializes the selected backend.
 *
 * @param backend The cryptographic backend to use
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_crypto_init(esp32_crypto_backend_t backend);

/**
 * @brief Deinitialize the ESP32 crypto library
 */
void esp32_crypto_deinit(void);

/**
 * @brief Check if hardware acceleration is available
 *
 * @return true if hardware acceleration is available and enabled
 */
bool esp32_crypto_hw_acceleration_available(void);

/**
 * @brief Get the current cryptographic backend
 *
 * @return The currently active backend
 */
esp32_crypto_backend_t esp32_crypto_get_backend(void);

/**
 * @brief AES encryption/decryption functions
 */

/**
 * @brief Initialize AES context
 *
 * @param ctx Pointer to AES context
 * @param key AES key
 * @param key_size Key size
 * @param mode AES mode
 * @param encrypt true for encryption, false for decryption
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_aes_init(esp32_aes_context_t** ctx,
                                    const uint8_t* key,
                                    esp32_crypto_aes_key_size_t key_size,
                                    esp32_crypto_aes_mode_t mode,
                                    bool encrypt);

/**
 * @brief Free AES context
 *
 * @param ctx AES context to free
 */
void esp32_aes_free(esp32_aes_context_t* ctx);

/**
 * @brief Set AES initialization vector (IV)
 *
 * @param ctx AES context
 * @param iv Initialization vector
 * @param iv_len IV length
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_aes_set_iv(esp32_aes_context_t* ctx,
                                      const uint8_t* iv,
                                      size_t iv_len);

/**
 * @brief Process AES data
 *
 * @param ctx AES context
 * @param input Input data
 * @param input_len Input data length
 * @param output Output buffer
 * @param output_len Pointer to output length (updated on return)
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_aes_process(esp32_aes_context_t* ctx,
                                       const uint8_t* input,
                                       size_t input_len,
                                       uint8_t* output,
                                       size_t* output_len);

/**
 * @brief SHA hash functions
 */

/**
 * @brief Initialize SHA context
 *
 * @param ctx Pointer to SHA context
 * @param type SHA algorithm type
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_sha_init(esp32_sha_context_t** ctx,
                                    esp32_crypto_sha_type_t type);

/**
 * @brief Free SHA context
 *
 * @param ctx SHA context to free
 */
void esp32_sha_free(esp32_sha_context_t* ctx);

/**
 * @brief Update SHA with data
 *
 * @param ctx SHA context
 * @param data Input data
 * @param data_len Data length
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_sha_update(esp32_sha_context_t* ctx,
                                      const uint8_t* data,
                                      size_t data_len);

/**
 * @brief Finalize SHA and get hash
 *
 * @param ctx SHA context
 * @param hash Output hash buffer
 * @param hash_len Pointer to hash length (updated on return)
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_sha_final(esp32_sha_context_t* ctx,
                                     uint8_t* hash,
                                     size_t* hash_len);

/**
 * @brief One-shot SHA computation
 *
 * @param type SHA algorithm type
 * @param data Input data
 * @param data_len Data length
 * @param hash Output hash buffer
 * @param hash_len Pointer to hash length (updated on return)
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_sha_compute(esp32_crypto_sha_type_t type,
                                       const uint8_t* data,
                                       size_t data_len,
                                       uint8_t* hash,
                                       size_t* hash_len);

/**
 * @brief ECC (Elliptic Curve Cryptography) functions
 */

/**
 * @brief Initialize ECC context
 *
 * @param ctx Pointer to ECC context
 * @param curve ECC curve type
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_ecc_init(esp32_ecc_context_t** ctx,
                                    esp32_crypto_ecc_curve_t curve);

/**
 * @brief Free ECC context
 *
 * @param ctx ECC context to free
 */
void esp32_ecc_free(esp32_ecc_context_t* ctx);

/**
 * @brief Generate ECC key pair
 *
 * @param ctx ECC context
 * @param private_key Output private key buffer
 * @param private_key_len Pointer to private key length (updated on return)
 * @param public_key Output public key buffer
 * @param public_key_len Pointer to public key length (updated on return)
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_ecc_generate_keypair(esp32_ecc_context_t* ctx,
                                                uint8_t* private_key,
                                                size_t* private_key_len,
                                                uint8_t* public_key,
                                                size_t* public_key_len);

/**
 * @brief Sign data using ECC
 *
 * @param ctx ECC context
 * @param private_key Private key
 * @param private_key_len Private key length
 * @param data Data to sign
 * @param data_len Data length
 * @param signature Output signature buffer
 * @param signature_len Pointer to signature length (updated on return)
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_ecc_sign(esp32_ecc_context_t* ctx,
                                    const uint8_t* private_key,
                                    size_t private_key_len,
                                    const uint8_t* data,
                                    size_t data_len,
                                    uint8_t* signature,
                                    size_t* signature_len);

/**
 * @brief Verify ECC signature
 *
 * @param ctx ECC context
 * @param public_key Public key
 * @param public_key_len Public key length
 * @param data Signed data
 * @param data_len Data length
 * @param signature Signature to verify
 * @param signature_len Signature length
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_ecc_verify(esp32_ecc_context_t* ctx,
                                      const uint8_t* public_key,
                                      size_t public_key_len,
                                      const uint8_t* data,
                                      size_t data_len,
                                      const uint8_t* signature,
                                      size_t signature_len);

/**
 * @brief Random number generation functions
 */

/**
 * @brief Initialize RNG context
 *
 * @param ctx Pointer to RNG context
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_rng_init(esp32_rng_context_t** ctx);

/**
 * @brief Free RNG context
 *
 * @param ctx RNG context to free
 */
void esp32_rng_free(esp32_rng_context_t* ctx);

/**
 * @brief Generate random bytes
 *
 * @param ctx RNG context
 * @param output Output buffer for random bytes
 * @param length Number of random bytes to generate
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_rng_generate(esp32_rng_context_t* ctx,
                                        uint8_t* output,
                                        size_t length);

/**
 * @brief Fill buffer with random bytes (one-shot)
 *
 * @param output Output buffer for random bytes
 * @param length Number of random bytes to generate
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_rng_fill(uint8_t* output, size_t length);

/**
 * @brief Secure boot functions (ESP32 specific)
 */

/**
 * @brief Verify secure boot signature
 *
 * @param image Firmware image
 * @param image_len Image length
 * @param signature Signature to verify
 * @param signature_len Signature length
 * @param public_key Public key for verification
 * @param public_key_len Public key length
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_secure_boot_verify(const uint8_t* image,
                                             size_t image_len,
                                             const uint8_t* signature,
                                             size_t signature_len,
                                             const uint8_t* public_key,
                                             size_t public_key_len);

/**
 * @brief Generate secure boot signature
 *
 * @param image Firmware image
 * @param image_len Image length
 * @param signature Output signature buffer
 * @param signature_len Pointer to signature length (updated on return)
 * @param private_key Private key for signing
 * @param private_key_len Private key length
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_secure_boot_sign(const uint8_t* image,
                                           size_t image_len,
                                           uint8_t* signature,
                                           size_t* signature_len,
                                           const uint8_t* private_key,
                                           size_t private_key_len);

/**
 * @brief Utility functions
 */

/**
 * @brief Get crypto library version
 *
 * @return Version string
 */
const char* esp32_crypto_version(void);

/**
 * @brief Get last error message
 *
 * @return Error message string
 */
const char* esp32_crypto_last_error(void);

/**
 * @brief Enable/disable FIPS mode (if supported by backend)
 *
 * @param enable true to enable FIPS mode, false to disable
 * @return ESP32_CRYPTO_SUCCESS on success, error code otherwise
 */
esp32_crypto_result_t esp32_crypto_enable_fips(bool enable);

#ifdef __cplusplus
}
#endif

#endif // ESP32_CRYPTO_H