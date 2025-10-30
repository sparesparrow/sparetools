"""
OpenSSL Tools Security Module

Security and compliance utilities for OpenSSL packages.
"""

from .sbom_generator import generate_openssl_sbom

__all__ = [
    'generate_openssl_sbom'
]