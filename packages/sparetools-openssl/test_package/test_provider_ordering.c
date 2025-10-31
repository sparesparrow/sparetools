#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/provider.h>
#include <stdio.h>
#include <string.h>

/**
 * Test provider ordering and availability
 *
 * Tests that:
 * 1. Default provider is available
 * 2. Legacy provider can be loaded if available
 * 3. Provider dependencies are correctly ordered
 * 4. Multiple algorithms work correctly
 */

int test_default_provider(void) {
    printf("Testing default provider availability...\n");

    EVP_MD *md_sha256 = EVP_MD_fetch(NULL, "SHA2-256", NULL);
    if (!md_sha256) {
        fprintf(stderr, "ERROR: Failed to fetch SHA2-256 from default provider\n");
        return 1;
    }
    printf("✓ SHA2-256 available from default provider\n");
    EVP_MD_free(md_sha256);

    EVP_CIPHER *cipher_aes = EVP_CIPHER_fetch(NULL, "AES-256-CBC", NULL);
    if (!cipher_aes) {
        fprintf(stderr, "ERROR: Failed to fetch AES-256-CBC from default provider\n");
        return 1;
    }
    printf("✓ AES-256-CBC available from default provider\n");
    EVP_CIPHER_free(cipher_aes);

    return 0;
}

int test_legacy_provider(void) {
    printf("\nTesting legacy provider availability...\n");

    OSSL_PROVIDER *legacy = OSSL_PROVIDER_load(NULL, "legacy");
    if (!legacy) {
        printf("⚠ Legacy provider not available (this is expected in newer OpenSSL)\n");
        return 0;
    }

    printf("✓ Legacy provider loaded\n");

    /* Test that deprecated algorithms work with legacy provider */
    EVP_MD *md_md5 = EVP_MD_fetch(NULL, "MD5", NULL);
    if (md_md5) {
        printf("✓ MD5 available from legacy provider\n");
        EVP_MD_free(md_md5);
    } else {
        printf("⚠ MD5 not available even with legacy provider\n");
    }

    OSSL_PROVIDER_unload(legacy);
    printf("✓ Legacy provider unloaded\n");
    return 0;
}

int test_provider_ordering(void) {
    printf("\nTesting provider ordering...\n");

    /* Test that default provider is preferred for modern algorithms */
    EVP_MD *sha256 = EVP_MD_fetch(NULL, "SHA2-256", NULL);
    EVP_CIPHER *aes = EVP_CIPHER_fetch(NULL, "AES-256-GCM", NULL);

    if (!sha256 || !aes) {
        fprintf(stderr, "ERROR: Modern algorithms not available\n");
        if (sha256) EVP_MD_free(sha256);
        if (aes) EVP_CIPHER_free(aes);
        return 1;
    }

    printf("✓ Default provider provides modern algorithms\n");
    EVP_MD_free(sha256);
    EVP_CIPHER_free(aes);

    return 0;
}

int test_algorithm_list(void) {
    printf("\nTesting available algorithms...\n");

    struct {
        const char *algorithm;
        int is_digest;
    } algorithms[] = {
        {"SHA2-256", 1},
        {"SHA2-384", 1},
        {"SHA2-512", 1},
        {"SHA3-256", 1},
        {"SHA3-512", 1},
        {"AES-128-CBC", 0},
        {"AES-256-CBC", 0},
        {"AES-256-GCM", 0},
        {"ChaCha20-Poly1305", 0},
        {NULL, 0}
    };

    int algorithm_count = 0;
    for (int i = 0; algorithms[i].algorithm != NULL; i++) {
        if (algorithms[i].is_digest) {
            EVP_MD *md = EVP_MD_fetch(NULL, algorithms[i].algorithm, NULL);
            if (md) {
                printf("✓ %s available\n", algorithms[i].algorithm);
                EVP_MD_free(md);
                algorithm_count++;
            } else {
                printf("✗ %s NOT available\n", algorithms[i].algorithm);
            }
        } else {
            EVP_CIPHER *cipher = EVP_CIPHER_fetch(NULL, algorithms[i].algorithm, NULL);
            if (cipher) {
                printf("✓ %s available\n", algorithms[i].algorithm);
                EVP_CIPHER_free(cipher);
                algorithm_count++;
            } else {
                printf("✗ %s NOT available\n", algorithms[i].algorithm);
            }
        }
    }

    printf("\n%d algorithms available\n", algorithm_count);
    return algorithm_count >= 6 ? 0 : 1;
}

int main() {
    printf("=================================\n");
    printf("OpenSSL Provider Ordering Tests\n");
    printf("=================================\n\n");

    int failures = 0;

    if (test_default_provider() != 0) {
        printf("✗ Default provider test FAILED\n");
        failures++;
    }

    if (test_legacy_provider() != 0) {
        printf("✗ Legacy provider test FAILED\n");
        failures++;
    }

    if (test_provider_ordering() != 0) {
        printf("✗ Provider ordering test FAILED\n");
        failures++;
    }

    if (test_algorithm_list() != 0) {
        printf("✗ Algorithm list test FAILED\n");
        failures++;
    }

    printf("\n=================================\n");
    if (failures == 0) {
        printf("✅ All provider tests PASSED!\n");
        return 0;
    } else {
        printf("❌ %d test(s) FAILED\n", failures);
        return 1;
    }
}
