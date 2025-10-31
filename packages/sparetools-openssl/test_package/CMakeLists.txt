cmake_minimum_required(VERSION 3.15)
project(test_openssl C)

find_package(OpenSSL REQUIRED)

# Basic OpenSSL test
add_executable(test_openssl test_openssl.c)
target_link_libraries(test_openssl OpenSSL::SSL OpenSSL::Crypto)

# Provider ordering tests
add_executable(test_provider_ordering test_provider_ordering.c)
target_link_libraries(test_provider_ordering OpenSSL::SSL OpenSSL::Crypto)

# FIPS smoke tests
add_executable(test_fips_smoke test_fips_smoke.c)
target_link_libraries(test_fips_smoke OpenSSL::SSL OpenSSL::Crypto)

# Enable testing
enable_testing()

# Add tests
add_test(NAME openssl_basic COMMAND test_openssl)
add_test(NAME openssl_provider_ordering COMMAND test_provider_ordering)
add_test(NAME openssl_fips_smoke COMMAND test_fips_smoke)

