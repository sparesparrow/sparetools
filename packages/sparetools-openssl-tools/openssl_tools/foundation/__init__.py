"""
OpenSSL Tools Foundation Module

Core foundation utilities for OpenSSL Conan ecosystem.
"""

from .version_manager import get_openssl_version, parse_openssl_version
from .profile_deployer import deploy_openssl_profiles, list_openssl_profiles

__all__ = [
    'get_openssl_version',
    'parse_openssl_version', 
    'deploy_openssl_profiles',
    'list_openssl_profiles'
]