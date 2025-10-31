#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <stdio.h>
#include <string.h>

int main() {
    printf("Testing SpareTools OpenSSL package...\n");
    
    /* Initialize OpenSSL */
    SSL_library_init();
    SSL_load_error_strings();
    OpenSSL_add_all_algorithms();
    
    /* Print OpenSSL version */
    printf("OpenSSL version: %s\n", OpenSSL_version(OPENSSL_VERSION));
    printf("OpenSSL built on: %s\n", OpenSSL_version(OPENSSL_BUILT_ON));
    printf("OpenSSL platform: %s\n", OpenSSL_version(OPENSSL_PLATFORM));
    
    /* Test basic cryptographic operations */
    const EVP_MD *md = EVP_sha256();
    if (md == NULL) {
        fprintf(stderr, "ERROR: Failed to get SHA-256 digest\n");
        return 1;
    }
    printf("SHA-256 digest algorithm: %s\n", EVP_MD_name(md));
    
    /* Test simple hash */
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (ctx == NULL) {
        fprintf(stderr, "ERROR: Failed to create EVP_MD_CTX\n");
        return 1;
    }
    
    const char *test_data = "Hello, SpareTools OpenSSL!";
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    
    if (!EVP_DigestInit_ex(ctx, md, NULL)) {
        fprintf(stderr, "ERROR: EVP_DigestInit_ex failed\n");
        EVP_MD_CTX_free(ctx);
        return 1;
    }
    
    if (!EVP_DigestUpdate(ctx, test_data, strlen(test_data))) {
        fprintf(stderr, "ERROR: EVP_DigestUpdate failed\n");
        EVP_MD_CTX_free(ctx);
        return 1;
    }
    
    if (!EVP_DigestFinal_ex(ctx, hash, &hash_len)) {
        fprintf(stderr, "ERROR: EVP_DigestFinal_ex failed\n");
        EVP_MD_CTX_free(ctx);
        return 1;
    }
    
    printf("SHA-256 hash of test data: ");
    for (unsigned int i = 0; i < hash_len; i++) {
        printf("%02x", hash[i]);
    }
    printf("\n");
    
    EVP_MD_CTX_free(ctx);
    
    /* Cleanup */
    EVP_cleanup();
    ERR_free_strings();
    
    printf("\n✅ All OpenSSL tests passed successfully!\n");
    return 0;
}

