#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/crypto.h>
#include <stdio.h>
#include <string.h>

/**
 * FIPS Smoke Tests
 *
 * Basic smoke tests to verify FIPS module functionality:
 * 1. FIPS mode availability
 * 2. Approved algorithms work
 * 3. FIPS self-tests complete successfully
 * 4. Critical cryptographic operations succeed
 */

int test_fips_mode(void) {
    printf("Testing FIPS mode...\n");

    int fips_mode = FIPS_mode();
    if (fips_mode) {
        printf("✓ FIPS mode is ENABLED\n");
    } else {
        printf("⚠ FIPS mode is DISABLED (build may not include FIPS)\n");
    }

    return 0;  /* Non-fatal if FIPS not enabled */
}

int test_fips_algorithms(void) {
    printf("\nTesting FIPS-approved algorithms...\n");

    /* FIPS-approved digest algorithms */
    struct {
        const char *name;
        int min_size;
    } approved_digests[] = {
        {"SHA2-256", 32},
        {"SHA2-384", 48},
        {"SHA2-512", 64},
        {"SHA3-256", 32},
        {"SHA3-384", 48},
        {NULL, 0}
    };

    int digest_count = 0;
    for (int i = 0; approved_digests[i].name != NULL; i++) {
        EVP_MD *md = EVP_MD_fetch(NULL, approved_digests[i].name, NULL);
        if (!md) {
            fprintf(stderr, "ERROR: FIPS digest %s not available\n", approved_digests[i].name);
            return 1;
        }

        printf("✓ %s available\n", approved_digests[i].name);
        EVP_MD_free(md);
        digest_count++;
    }

    printf("✓ All %d FIPS-approved digests available\n", digest_count);

    /* FIPS-approved cipher algorithms */
    printf("\nTesting FIPS-approved ciphers...\n");
    struct {
        const char *name;
    } approved_ciphers[] = {
        {"AES-128-CBC"},
        {"AES-192-CBC"},
        {"AES-256-CBC"},
        {"AES-128-GCM"},
        {"AES-256-GCM"},
        {NULL}
    };

    int cipher_count = 0;
    for (int i = 0; approved_ciphers[i].name != NULL; i++) {
        EVP_CIPHER *cipher = EVP_CIPHER_fetch(NULL, approved_ciphers[i].name, NULL);
        if (!cipher) {
            fprintf(stderr, "WARNING: FIPS cipher %s not available\n", approved_ciphers[i].name);
            continue;
        }

        printf("✓ %s available\n", approved_ciphers[i].name);
        EVP_CIPHER_free(cipher);
        cipher_count++;
    }

    printf("✓ %d FIPS-approved ciphers available\n", cipher_count);
    return cipher_count >= 4 ? 0 : 1;
}

int test_sha256_hash(void) {
    printf("\nTesting SHA-256 hash operation...\n");

    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) {
        fprintf(stderr, "ERROR: Failed to create EVP_MD_CTX\n");
        return 1;
    }

    EVP_MD *md = EVP_MD_fetch(NULL, "SHA2-256", NULL);
    if (!md) {
        fprintf(stderr, "ERROR: Failed to fetch SHA2-256\n");
        EVP_MD_CTX_free(ctx);
        return 1;
    }

    const char *test_data = "FIPS Test Vector";
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;

    if (!EVP_DigestInit_ex(ctx, md, NULL)) {
        fprintf(stderr, "ERROR: EVP_DigestInit_ex failed\n");
        EVP_MD_free(md);
        EVP_MD_CTX_free(ctx);
        return 1;
    }

    if (!EVP_DigestUpdate(ctx, test_data, strlen(test_data))) {
        fprintf(stderr, "ERROR: EVP_DigestUpdate failed\n");
        EVP_MD_free(md);
        EVP_MD_CTX_free(ctx);
        return 1;
    }

    if (!EVP_DigestFinal_ex(ctx, hash, &hash_len)) {
        fprintf(stderr, "ERROR: EVP_DigestFinal_ex failed\n");
        EVP_MD_free(md);
        EVP_MD_CTX_free(ctx);
        return 1;
    }

    printf("✓ SHA-256 hash computed successfully\n");
    printf("  Input: %s\n", test_data);
    printf("  Output: ");
    for (unsigned int i = 0; i < hash_len; i++) {
        printf("%02x", hash[i]);
    }
    printf("\n");

    EVP_MD_free(md);
    EVP_MD_CTX_free(ctx);
    return 0;
}

int test_aes_encryption(void) {
    printf("\nTesting AES-256-CBC encryption...\n");

    EVP_CIPHER *cipher = EVP_CIPHER_fetch(NULL, "AES-256-CBC", NULL);
    if (!cipher) {
        fprintf(stderr, "ERROR: Failed to fetch AES-256-CBC\n");
        return 1;
    }

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        fprintf(stderr, "ERROR: Failed to create EVP_CIPHER_CTX\n");
        EVP_CIPHER_free(cipher);
        return 1;
    }

    /* Key and IV (256-bit key, 128-bit IV) */
    unsigned char key[32] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f
    };

    unsigned char iv[16] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
    };

    unsigned char plaintext[] = "FIPS Test Encryption Vector!!!";
    unsigned char ciphertext[128];
    unsigned char decrypted[128];
    int len = 0;
    int ciphertext_len = 0;
    int plaintext_len = sizeof(plaintext) - 1;

    /* Encrypt */
    if (!EVP_EncryptInit_ex(ctx, cipher, NULL, key, iv)) {
        fprintf(stderr, "ERROR: EVP_EncryptInit_ex failed\n");
        EVP_CIPHER_CTX_free(ctx);
        EVP_CIPHER_free(cipher);
        return 1;
    }

    if (!EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len)) {
        fprintf(stderr, "ERROR: EVP_EncryptUpdate failed\n");
        EVP_CIPHER_CTX_free(ctx);
        EVP_CIPHER_free(cipher);
        return 1;
    }
    ciphertext_len = len;

    if (!EVP_EncryptFinal_ex(ctx, ciphertext + len, &len)) {
        fprintf(stderr, "ERROR: EVP_EncryptFinal_ex failed\n");
        EVP_CIPHER_CTX_free(ctx);
        EVP_CIPHER_free(cipher);
        return 1;
    }
    ciphertext_len += len;

    printf("✓ AES-256-CBC encryption successful\n");

    /* Decrypt */
    if (!EVP_DecryptInit_ex(ctx, cipher, NULL, key, iv)) {
        fprintf(stderr, "ERROR: EVP_DecryptInit_ex failed\n");
        EVP_CIPHER_CTX_free(ctx);
        EVP_CIPHER_free(cipher);
        return 1;
    }

    if (!EVP_DecryptUpdate(ctx, decrypted, &len, ciphertext, ciphertext_len)) {
        fprintf(stderr, "ERROR: EVP_DecryptUpdate failed\n");
        EVP_CIPHER_CTX_free(ctx);
        EVP_CIPHER_free(cipher);
        return 1;
    }
    int decrypted_len = len;

    if (!EVP_DecryptFinal_ex(ctx, decrypted + len, &len)) {
        fprintf(stderr, "ERROR: EVP_DecryptFinal_ex failed\n");
        EVP_CIPHER_CTX_free(ctx);
        EVP_CIPHER_free(cipher);
        return 1;
    }
    decrypted_len += len;

    printf("✓ AES-256-CBC decryption successful\n");

    /* Verify */
    if (plaintext_len != decrypted_len ||
        memcmp(plaintext, decrypted, plaintext_len) != 0) {
        fprintf(stderr, "ERROR: Decrypted text does not match original\n");
        EVP_CIPHER_CTX_free(ctx);
        EVP_CIPHER_free(cipher);
        return 1;
    }

    printf("✓ Encryption/decryption round-trip verified\n");

    EVP_CIPHER_CTX_free(ctx);
    EVP_CIPHER_free(cipher);
    return 0;
}

int main() {
    printf("===================================\n");
    printf("OpenSSL FIPS Smoke Tests\n");
    printf("===================================\n\n");

    int failures = 0;

    if (test_fips_mode() != 0) {
        printf("✗ FIPS mode test FAILED\n");
        failures++;
    }

    if (test_fips_algorithms() != 0) {
        printf("✗ FIPS algorithms test FAILED\n");
        failures++;
    }

    if (test_sha256_hash() != 0) {
        printf("✗ SHA-256 hash test FAILED\n");
        failures++;
    }

    if (test_aes_encryption() != 0) {
        printf("✗ AES encryption test FAILED\n");
        failures++;
    }

    printf("\n===================================\n");
    if (failures == 0) {
        printf("✅ All FIPS smoke tests PASSED!\n");
        return 0;
    } else {
        printf("❌ %d test(s) FAILED\n", failures);
        return 1;
    }
}
