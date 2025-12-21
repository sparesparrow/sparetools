# Enterprise Security Hardening Guide

## Overview

This guide outlines the comprehensive security hardening measures implemented in the SpareTools ↔ NucleusESP32 integration, achieving enterprise-grade security for ESP32-based embedded systems.

## Security Architecture

### Defense in Depth

The security implementation follows a defense-in-depth approach with multiple layers:

```
┌─────────────────┐
│   Application   │ Application-level security
├─────────────────┤
│  Cryptographic  │ Hardware-accelerated crypto
├─────────────────┤
│   Firmware      │ Secure boot, flash encryption
├─────────────────┤
│   Hardware      │ ESP32 security features
└─────────────────┘
```

### Security Components

1. **Cryptographic Suite**: Hardware-accelerated encryption, signing, and verification
2. **Secure Boot**: Firmware integrity verification
3. **Flash Encryption**: Firmware confidentiality protection
4. **Access Controls**: Permission-based resource access
5. **Audit Logging**: Security event monitoring

## Cryptographic Implementation

### Hardware Acceleration

The ESP32 provides hardware acceleration for cryptographic operations:

```cpp
// Initialize with hardware acceleration
esp32_crypto_result_t result = esp32_crypto_init(ESP32_CRYPTO_BACKEND_MBEDTLS);

// Hardware-accelerated AES
#define CONFIG_MBEDTLS_HARDWARE_AES 1
#define CONFIG_MBEDTLS_HARDWARE_MPI 1
#define CONFIG_MBEDTLS_HARDWARE_SHA 1
```

### Security Profiles

#### Basic Security Profile
```json
{
  "name": "basic_security",
  "crypto_backend": "mbedTLS",
  "algorithms": {
    "aes": {"key_sizes": ["AES_256"], "modes": ["CBC", "GCM"]},
    "sha": ["SHA_256"],
    "ecc": ["P256"],
    "rng": true
  },
  "hardware_acceleration": true,
  "secure_boot": false,
  "flash_encryption": false,
  "fips_mode": false
}
```

#### Enterprise Security Profile
```json
{
  "name": "enterprise_security",
  "crypto_backend": "mbedTLS",
  "algorithms": {
    "aes": {"key_sizes": ["AES_256"], "modes": ["CBC", "GCM", "CTR"]},
    "sha": ["SHA_256", "SHA_384", "SHA_512"],
    "ecc": ["P256", "P384", "P521"],
    "rng": true,
    "hmac": true,
    "hkdf": true
  },
  "hardware_acceleration": true,
  "secure_boot": true,
  "flash_encryption": true,
  "fips_mode": true,
  "certificate_validation": true,
  "key_derivation": true
}
```

### Key Management

#### Secure Key Storage
```cpp
// Generate and store ECC key pair
esp32_ecc_context_t* ecc_ctx;
esp32_ecc_init(&ecc_ctx, ESP32_CRYPTO_ECC_P256);

uint8_t private_key[32];
uint8_t public_key[64];
size_t priv_len, pub_len;

esp32_ecc_generate_keypair(ecc_ctx, private_key, &priv_len, public_key, &pub_len);

// Secure key storage (platform-specific implementation)
// Keys should be stored in encrypted flash or secure element
```

#### Key Derivation
```cpp
// HKDF key derivation for multiple keys from one master key
uint8_t master_key[32] = { /* master key */ };
uint8_t salt[16] = { /* salt */ };
uint8_t info[] = "encryption_key";
uint8_t derived_key[32];

esp32_crypto_result_t result = esp32_hkdf_derive(
    ESP32_CRYPTO_SHA_256,
    master_key, sizeof(master_key),
    salt, sizeof(salt),
    info, strlen((char*)info),
    derived_key, sizeof(derived_key)
);
```

## Secure Boot Implementation

### Overview

Secure boot ensures only authenticated firmware can execute on the device.

### Configuration
```ini
; platformio.ini
board_build.secure_boot = true
board_build.flash_encryption = true
board_build.partitions = partitions_secure.csv
```

### Implementation
```cpp
// Verify firmware signature during boot
esp32_crypto_result_t verify_firmware(const uint8_t* firmware, size_t len,
                                    const uint8_t* signature, size_t sig_len,
                                    const uint8_t* public_key, size_t key_len) {
    return esp32_secure_boot_verify(firmware, len, signature, sig_len,
                                  public_key, key_len);
}

// Sign firmware for secure boot
esp32_crypto_result_t sign_firmware(const uint8_t* firmware, size_t len,
                                  uint8_t* signature, size_t* sig_len,
                                  const uint8_t* private_key, size_t key_len) {
    return esp32_secure_boot_sign(firmware, len, signature, sig_len,
                                private_key, key_len);
}
```

### Build Integration
```bash
# Generate secure boot keys (development only)
espsecure.py generate_signing_key secure_boot_key.pem

# Sign firmware
espsecure.py sign_data --keyfile secure_boot_key.pem \
                      --output firmware_signed.bin \
                      firmware.bin

# Flash with secure boot
esptool.py --chip esp32s3 \
           --port /dev/ttyUSB0 \
           --baud 921600 \
           --before default_reset \
           --after hard_reset \
           write_flash --encrypt \
           --flash_mode dio \
           --flash_freq 80m \
           --flash_size 4MB \
           0x0 bootloader.bin \
           0x8000 partitions_secure.bin \
           0x10000 firmware_signed.bin
```

## Flash Encryption

### Configuration
```cpp
// ESP-IDF configuration
#define CONFIG_SECURE_BOOT_ENABLE 1
#define CONFIG_FLASH_ENCRYPTION_ENABLE 1
#define CONFIG_SECURE_BOOT_ALLOW_JTAG 0
#define CONFIG_SECURE_BOOT_ALLOW_EFUSE_RD_DIS 1
```

### Automatic Encryption
```bash
# Enable flash encryption
espefuse.py --port /dev/ttyUSB0 burn_efuse FLASH_CRYPT_CNT

# Flash encrypted firmware
esptool.py --chip esp32s3 \
           write_flash --encrypt \
           0x10000 firmware.bin
```

### Key Management
```cpp
// Generate flash encryption key
uint8_t flash_key[32];
esp32_rng_fill(flash_key, sizeof(flash_key));

// Store key securely (development only - production uses hardware)
esp32_secure_store_key(flash_key, sizeof(flash_key), "flash_encryption_key");
```

## Runtime Security

### Stack Protection
```cpp
// Compiler flags for stack protection
#pragma GCC optimize("-fstack-protector-strong")
#pragma GCC optimize("-fstack-clash-protection")
#pragma GCC optimize("-fcf-protection")

// Runtime stack checks
void __stack_chk_fail(void) {
    // Handle stack overflow
    esp_restart();  // Reset device
}
```

### Address Space Layout Randomization
```cpp
// Enable ASLR (ESP-IDF specific)
#define CONFIG_MPU_ENABLE 1
#define CONFIG_MPU_REGION_SIZE 0x10000

// Memory protection
esp_mpu_config_t mpu_config = {
    .region_num = 1,
    .start_addr = 0x40000000,
    .end_addr = 0x40010000,
    .access = ESP_MPU_ACCESS_R,
    .executable = false
};
esp_mpu_configure(&mpu_config);
```

### Non-Executable Memory
```cpp
// Mark data sections as non-executable
__attribute__((section(".rodata"))) const char ro_data[] = "read-only";
__attribute__((section(".data"))) char rw_data[1024];

// ESP-IDF memory protection
esp_mpu_region_t regions[] = {
    {
        .start = 0x3FC00000,  // Data RAM
        .size = ESP_MPU_REGION_SIZE_512KB,
        .access = ESP_MPU_ACCESS_RW,
        .executable = false
    },
    {
        .start = 0x40000000,  // IRAM
        .size = ESP_MPU_REGION_SIZE_512KB,
        .access = ESP_MPU_ACCESS_RW,
        .executable = true
    }
};
esp_mpu_set_regions(regions, sizeof(regions)/sizeof(esp_mpu_region_t));
```

## Security Monitoring

### Audit Logging
```cpp
// Security event logging
typedef enum {
    SECURITY_EVENT_BOOT,
    SECURITY_EVENT_CRYPTO_OP,
    SECURITY_EVENT_ACCESS_DENIED,
    SECURITY_EVENT_FIRMWARE_UPDATE,
    SECURITY_EVENT_SECURE_BOOT_VERIFY
} security_event_t;

void log_security_event(security_event_t event, const char* details) {
    // Store in secure flash or send to monitoring system
    esp_log_write(ESP_LOG_INFO, "SECURITY",
                 "Event: %d, Details: %s, Time: %llu",
                 event, details, esp_timer_get_time());
}

// Example usage
log_security_event(SECURITY_EVENT_SECURE_BOOT_VERIFY, "Firmware signature verified");
```

### Integrity Checking
```cpp
// Runtime integrity verification
bool verify_memory_integrity(const void* ptr, size_t size, const uint8_t* expected_hash) {
    uint8_t actual_hash[32];
    size_t hash_len;

    esp32_crypto_result_t result = esp32_sha_compute(
        ESP32_CRYPTO_SHA_256, (const uint8_t*)ptr, size,
        actual_hash, &hash_len
    );

    if (result != ESP32_CRYPTO_SUCCESS) {
        log_security_event(SECURITY_EVENT_ACCESS_DENIED, "Integrity check failed");
        return false;
    }

    return memcmp(actual_hash, expected_hash, 32) == 0;
}
```

## CI/CD Security

### Automated Security Scanning

#### Secret Detection
```yaml
- name: Secret scanning
  uses: zricethezav/gitleaks-action@main
  with:
    config-path: .gitleaks.toml

- name: TruffleHog scan
  run: |
    trufflehog3 --format json --output trufflehog-results.json .
```

#### Dependency Vulnerability Scanning
```yaml
- name: SCA analysis
  run: |
    # Scan Conan dependencies
    conan inspect . > conan-deps.txt
    grep -i "vulnerable\|exploit\|cve" conan-deps.txt || true

    # Generate SBOM
    cyclonedx-conan --conanfile conanfile.py --output sbom.json
```

#### Firmware Security Analysis
```yaml
- name: Firmware analysis
  run: |
    # Binary security checks
    binwalk firmware.bin > binwalk-report.txt
    esptool.py image_info firmware.bin > image-info.txt

    # Check for debug symbols
    if strings firmware.bin | grep -i "debug\|symbol"; then
        echo "❌ Debug symbols found in production firmware"
        exit 1
    fi
```

### Secure Build Environment

#### Build Secrets Management
```yaml
# GitHub Secrets
env:
  CONAN_TOKEN: ${{ secrets.CONAN_TOKEN }}
  SIGNING_KEY: ${{ secrets.SIGNING_KEY }}

# Secure key handling
- name: Setup signing keys
  run: |
    echo "$SIGNING_KEY" | base64 -d > secure_boot_key.pem
    chmod 600 secure_boot_key.pem
```

#### Build Attestation
```yaml
- name: Generate build attestation
  run: |
    # Create build manifest
    cat > build-attestation.json << EOF
    {
      "build_id": "${{ github.run_id }}",
      "commit": "${{ github.sha }}",
      "timestamp": "$(date -Iseconds)",
      "builder": "${{ github.actor }}",
      "firmware_hash": "$(sha256sum firmware.bin | cut -d' ' -f1)",
      "security_profile": "enterprise"
    }
    EOF

    # Sign attestation
    openssl dgst -sha256 -sign secure_boot_key.pem \
             -out build-attestation.sig build-attestation.json
```

## Threat Modeling

### Attack Vectors

#### Physical Attacks
- **JTAG Debug Access**: Disabled in production builds
- **Flash Dumping**: Mitigated by flash encryption
- **Side Channel Attacks**: Protected by hardware acceleration

#### Network Attacks
- **Firmware Updates**: Verified with secure boot
- **Man-in-the-Middle**: TLS with certificate pinning
- **Replay Attacks**: Timestamp and nonce validation

#### Software Attacks
- **Buffer Overflows**: Stack canaries and ASLR
- **Code Injection**: NX memory and DEP
- **Privilege Escalation**: Access control lists

### Risk Mitigation

#### STRIDE Threat Analysis

| Threat Type | Description | Mitigation |
|-------------|-------------|------------|
| Spoofing | Impersonation attacks | Certificate-based authentication |
| Tampering | Data modification | Cryptographic signatures |
| Repudiation | Action denial | Audit logging |
| Information Disclosure | Data leakage | Encryption at rest/transit |
| Denial of Service | Resource exhaustion | Rate limiting, watchdog timers |
| Elevation of Privilege | Unauthorized access | Access control, sandboxing |

## Compliance

### Security Standards

#### NIST SP 800-193
Platform Firmware Resiliency Guidelines compliance:
- Secure boot implementation
- Firmware integrity verification
- Recovery mechanisms

#### ISO 27001
Information security management:
- Risk assessment procedures
- Security control implementation
- Continuous monitoring

#### FIPS 140-2/3
Cryptographic module validation:
- Approved algorithms only
- Key management requirements
- Self-test capabilities

### Certification Preparation

#### Common Criteria (CC)
```yaml
# Security target definition
security_targets:
  - secure_boot: true
  - flash_encryption: true
  - cryptographic_services: hardware_accelerated
  - audit_logging: enabled
  - trusted_path: established
```

#### Penetration Testing Checklist
- [ ] Physical security assessment
- [ ] Firmware reverse engineering
- [ ] Side channel analysis
- [ ] Network protocol analysis
- [ ] Cryptographic implementation review
- [ ] Supply chain security assessment

## Performance Impact

### Security vs Performance Trade-offs

| Security Feature | Performance Impact | Recommendation |
|------------------|-------------------|----------------|
| Secure Boot | +2-5% boot time | Always enabled |
| Flash Encryption | +1-3% access time | Enabled for sensitive data |
| Hardware Crypto | -10-20% vs software | Always use hardware |
| Stack Protection | +5-10% memory usage | Enabled in development |
| ASLR | Minimal impact | Enabled where supported |

### Optimization Strategies

#### Selective Security
```cpp
#ifdef CONFIG_SECURITY_LEVEL_ENTERPRISE
    // Enterprise security features
    enable_secure_boot();
    enable_flash_encryption();
    enable_stack_protection();
#endif

#ifdef CONFIG_SECURITY_LEVEL_BASIC
    // Basic security features only
    enable_secure_boot();
#endif
```

#### Performance Monitoring
```cpp
// Benchmark cryptographic operations
uint32_t start_time = esp_timer_get_time();

// Perform crypto operation
esp32_aes_process(aes_ctx, input, len, output, &out_len);

uint32_t end_time = esp_timer_get_time();
uint32_t duration_us = end_time - start_time;

// Log performance metrics
ESP_LOGI("CRYPTO", "AES operation: %u us", duration_us);
```

## Troubleshooting

### Common Security Issues

#### Secure Boot Failures
```bash
# Check secure boot configuration
espefuse.py --port /dev/ttyUSB0 summary

# Verify firmware signature
espsecure.py verify_signature --keyfile public_key.pem firmware.bin
```

#### Encryption Problems
```bash
# Check flash encryption status
espefuse.py --port /dev/ttyUSB0 summary | grep FLASH_CRYPT

# Decrypt firmware for analysis (development only)
esptool.py --chip esp32s3 decrypt_flash \
           --address 0x10000 --length 0x100000 \
           --output decrypted.bin encrypted_flash.bin
```

#### Performance Issues
```cpp
// Debug cryptographic performance
#define CRYPTO_PERF_DEBUG 1

#ifdef CRYPTO_PERF_DEBUG
#define CRYPTO_START_TIMING() uint32_t crypto_start = esp_timer_get_time()
#define CRYPTO_END_TIMING(msg) \
    uint32_t crypto_end = esp_timer_get_time(); \
    ESP_LOGI("CRYPTO_PERF", "%s: %u us", msg, crypto_end - crypto_start)
#else
#define CRYPTO_START_TIMING()
#define CRYPTO_END_TIMING(msg)
#endif
```

## Future Enhancements

### Advanced Security Features

#### Trusted Platform Module (TPM)
- Hardware-based key storage
- Secure key generation
- Attestation capabilities

#### Secure Enclave
- Isolated execution environment
- Secure key operations
- Runtime integrity monitoring

#### Zero Trust Architecture
- Continuous authentication
- Least privilege access
- Micro-segmentation

### Security Automation

#### Automated Vulnerability Scanning
```yaml
# Daily vulnerability scans
- cron: '0 2 * * *'
  jobs:
    vulnerability-scan:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - run: |
            # Automated security assessment
            ./scripts/security-assessment.sh
```

#### Security Policy as Code
```hcl
# Security policy definition
security_policy {
  encryption {
    algorithm = "AES-256-GCM"
    key_rotation = "90 days"
  }

  secure_boot {
    enabled = true
    key_rotation = "365 days"
  }

  audit {
    enabled = true
    retention = "7 years"
  }
}
```

---

This security hardening guide provides a comprehensive framework for enterprise-grade security in ESP32-based systems. The layered approach ensures robust protection while maintaining performance and usability.