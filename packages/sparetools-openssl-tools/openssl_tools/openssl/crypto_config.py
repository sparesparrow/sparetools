#!/usr/bin/env python3
"""
Cryptographic Configuration Manager for OpenSSL

This module provides comprehensive management of OpenSSL cryptographic configurations,
including FIPS settings, algorithm enablement, and security policy enforcement.
"""

import configparser
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, NamedTuple
from dataclasses import dataclass, field
from enum import Enum


class SecurityLevel(Enum):
    """OpenSSL security levels."""
    LEVEL_0 = 0  # All algorithms enabled
    LEVEL_1 = 1  # Weak algorithms disabled
    LEVEL_2 = 2  # Legacy algorithms disabled
    LEVEL_3 = 3  # Only modern algorithms enabled


class CipherSuite(Enum):
    """Predefined cipher suite configurations."""
    MODERN = "modern"
    INTERMEDIATE = "intermediate"
    LEGACY = "legacy"
    FIPS = "fips"


@dataclass
class CryptoConfiguration:
    """Complete cryptographic configuration."""
    security_level: SecurityLevel = SecurityLevel.LEVEL_1
    enabled_algorithms: Set[str] = field(default_factory=lambda: {
        "AES", "RSA", "ECDSA", "SHA256", "SHA384", "SHA512", "HMAC"
    })
    disabled_algorithms: Set[str] = field(default_factory=lambda: {
        "MD5", "RC4", "DES", "3DES"
    })
    min_key_sizes: Dict[str, int] = field(default_factory=lambda: {
        "RSA": 2048,
        "AES": 128,
        "ECDSA": 256
    })
    cipher_suites: CipherSuite = CipherSuite.INTERMEDIATE
    fips_enabled: bool = False
    tls_versions: Set[str] = field(default_factory=lambda: {
        "TLSv1.2", "TLSv1.3"
    })
    custom_options: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "security_level": self.security_level.value,
            "enabled_algorithms": list(self.enabled_algorithms),
            "disabled_algorithms": list(self.disabled_algorithms),
            "min_key_sizes": self.min_key_sizes,
            "cipher_suites": self.cipher_suites.value,
            "fips_enabled": self.fips_enabled,
            "tls_versions": list(self.tls_versions),
            "custom_options": self.custom_options
        }


class CryptoConfigManager:
    """
    Cryptographic configuration manager for OpenSSL.

    This class provides comprehensive management of OpenSSL cryptographic
    configurations, including algorithm enablement, security levels, and
    FIPS compliance settings.
    """

    # Default cipher suites by configuration type
    CIPHER_SUITES = {
        CipherSuite.MODERN: [
            "ECDHE-ECDSA-AES256-GCM-SHA384",
            "ECDHE-RSA-AES256-GCM-SHA384",
            "ECDHE-ECDSA-AES128-GCM-SHA256",
            "ECDHE-RSA-AES128-GCM-SHA256"
        ],
        CipherSuite.INTERMEDIATE: [
            "ECDHE-ECDSA-AES256-GCM-SHA384",
            "ECDHE-RSA-AES256-GCM-SHA384",
            "ECDHE-ECDSA-AES128-GCM-SHA256",
            "ECDHE-RSA-AES128-GCM-SHA256",
            "ECDHE-ECDSA-AES256-SHA384",
            "ECDHE-RSA-AES256-SHA384"
        ],
        CipherSuite.LEGACY: [
            "ECDHE-ECDSA-AES256-GCM-SHA384",
            "ECDHE-RSA-AES256-GCM-SHA384",
            "ECDHE-ECDSA-AES128-GCM-SHA256",
            "ECDHE-RSA-AES128-GCM-SHA256",
            "ECDHE-ECDSA-AES256-SHA384",
            "ECDHE-RSA-AES256-SHA384",
            "AES256-GCM-SHA384",
            "AES128-GCM-SHA256"
        ],
        CipherSuite.FIPS: [
            "ECDHE-ECDSA-AES256-GCM-SHA384",
            "ECDHE-RSA-AES256-GCM-SHA384",
            "ECDHE-ECDSA-AES128-GCM-SHA256",
            "ECDHE-RSA-AES128-GCM-SHA256"
        ]
    }

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the crypto configuration manager.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or self._find_default_config()
        self.current_config = self._load_configuration()

    def _find_default_config(self) -> str:
        """Find the default configuration file."""
        possible_paths = [
            Path.cwd() / "openssl_crypto.conf",
            Path.cwd() / ".openssl" / "crypto.conf",
            Path.home() / ".openssl_crypto.conf",
            "/etc/ssl/openssl_crypto.conf"
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        return str(Path.cwd() / "openssl_crypto.conf")

    def _load_configuration(self) -> CryptoConfiguration:
        """Load configuration from file or create default."""
        if not os.path.exists(self.config_file):
            return CryptoConfiguration()

        config = configparser.ConfigParser()
        config.read(self.config_file)

        crypto_config = CryptoConfiguration()

        if 'security' in config:
            sec = config['security']
            if 'level' in sec:
                crypto_config.security_level = SecurityLevel(int(sec['level']))

        if 'algorithms' in config:
            alg = config['algorithms']
            if 'enabled' in alg:
                crypto_config.enabled_algorithms = set(alg['enabled'].split(','))
            if 'disabled' in alg:
                crypto_config.disabled_algorithms = set(alg['disabled'].split(','))

        if 'key_sizes' in config:
            ks = config['key_sizes']
            for alg in ['RSA', 'AES', 'ECDSA']:
                if alg in ks:
                    crypto_config.min_key_sizes[alg] = int(ks[alg])

        if 'cipher_suites' in config:
            cs = config['cipher_suites']
            if 'profile' in cs:
                crypto_config.cipher_suites = CipherSuite(cs['profile'])

        if 'fips' in config:
            fips = config['fips']
            crypto_config.fips_enabled = fips.getboolean('enabled', False)

        if 'tls' in config:
            tls = config['tls']
            if 'versions' in tls:
                crypto_config.tls_versions = set(tls['versions'].split(','))

        return crypto_config

    def save_configuration(self, config_path: Optional[str] = None) -> None:
        """
        Save current configuration to file.

        Args:
            config_path: Path to save configuration (optional)
        """
        save_path = config_path or self.config_file

        config = configparser.ConfigParser()
        config.add_section('security')
        config.set('security', 'level', str(self.current_config.security_level.value))

        config.add_section('algorithms')
        config.set('algorithms', 'enabled', ','.join(self.current_config.enabled_algorithms))
        config.set('algorithms', 'disabled', ','.join(self.current_config.disabled_algorithms))

        config.add_section('key_sizes')
        for alg, size in self.current_config.min_key_sizes.items():
            config.set('key_sizes', alg, str(size))

        config.add_section('cipher_suites')
        config.set('cipher_suites', 'profile', self.current_config.cipher_suites.value)

        config.add_section('fips')
        config.set('fips', 'enabled', str(self.current_config.fips_enabled))

        config.add_section('tls')
        config.set('tls', 'versions', ','.join(self.current_config.tls_versions))

        # Create directory if it doesn't exist
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'w') as f:
            config.write(f)

        print(f"Configuration saved to: {save_path}")

    def apply_security_level(self, level: SecurityLevel) -> None:
        """
        Apply a security level configuration.

        Args:
            level: Security level to apply
        """
        self.current_config.security_level = level

        # Configure algorithms based on security level
        if level == SecurityLevel.LEVEL_0:
            # All algorithms enabled
            self.current_config.disabled_algorithms = set()
        elif level == SecurityLevel.LEVEL_1:
            # Disable weak algorithms
            self.current_config.disabled_algorithms = {"MD5", "RC4"}
        elif level == SecurityLevel.LEVEL_2:
            # Disable legacy algorithms
            self.current_config.disabled_algorithms = {"MD5", "RC4", "DES", "3DES"}
        elif level == SecurityLevel.LEVEL_3:
            # Only modern algorithms
            self.current_config.disabled_algorithms = {
                "MD5", "RC4", "DES", "3DES", "SHA1"
            }
            self.current_config.enabled_algorithms = {
                "AES", "RSA", "ECDSA", "SHA256", "SHA384", "SHA512", "HMAC"
            }

        # Update minimum key sizes based on security level
        if level >= SecurityLevel.LEVEL_2:
            self.current_config.min_key_sizes.update({
                "RSA": 2048,
                "AES": 128,
                "ECDSA": 256
            })

    def enable_fips_mode(self) -> None:
        """Enable FIPS mode configuration."""
        self.current_config.fips_enabled = True
        self.current_config.cipher_suites = CipherSuite.FIPS
        self.current_config.security_level = SecurityLevel.LEVEL_2

        # FIPS-required algorithms only
        self.current_config.enabled_algorithms = {
            "AES", "RSA", "ECDSA", "SHA256", "SHA384", "SHA512", "HMAC"
        }
        self.current_config.disabled_algorithms = {
            "MD5", "RC4", "DES", "3DES", "SHA1"
        }

    def disable_fips_mode(self) -> None:
        """Disable FIPS mode configuration."""
        self.current_config.fips_enabled = False
        self.current_config.cipher_suites = CipherSuite.INTERMEDIATE

    def get_cipher_suite_list(self) -> List[str]:
        """
        Get the list of cipher suites for current configuration.

        Returns:
            List of cipher suite strings
        """
        return self.CIPHER_SUITES[self.current_config.cipher_suites].copy()

    def generate_openssl_config(self, output_path: str) -> None:
        """
        Generate an OpenSSL configuration file based on current settings.

        Args:
            output_path: Path to save the OpenSSL configuration
        """
        config_lines = [
            "# OpenSSL Configuration Generated by CryptoConfigManager",
            "# Security Level: " + str(self.current_config.security_level.value),
            "",
            "[openssl_init]",
            "providers = provider_sect",
            "",
            "[provider_sect]",
            "default = default_sect",
            "legacy = legacy_sect",
        ]

        if self.current_config.fips_enabled:
            config_lines.extend([
                "fips = fips_sect",
                "",
                "[fips_sect]",
                "activate = 1"
            ])

        config_lines.extend([
            "",
            "[default_sect]",
            "activate = 1",
            "",
            "[legacy_sect]",
            "activate = 1"
        ])

        # Add algorithm restrictions based on security level
        if self.current_config.security_level >= SecurityLevel.LEVEL_1:
            config_lines.extend([
                "",
                "[alg_section]",
                "rsa_min_key_size = " + str(self.current_config.min_key_sizes["RSA"]),
                "ecdsa_min_key_size = " + str(self.current_config.min_key_sizes["ECDSA"]),
            ])

        # Disable weak ciphers
        disabled_ciphers = []
        if "MD5" in self.current_config.disabled_algorithms:
            disabled_ciphers.append("MD5")
        if "RC4" in self.current_config.disabled_algorithms:
            disabled_ciphers.append("RC4")

        if disabled_ciphers:
            config_lines.extend([
                "",
                "[cipher_sect]",
                "CIPHER = ALL:!{}".format(":!".join(disabled_ciphers))
            ])

        # Write configuration file
        with open(output_path, 'w') as f:
            f.write('\n'.join(config_lines))

        print(f"OpenSSL configuration generated: {output_path}")

    def validate_configuration(self) -> List[str]:
        """
        Validate the current configuration for consistency and security.

        Returns:
            List of validation warnings/errors
        """
        warnings = []

        # Check for conflicting settings
        if self.current_config.fips_enabled:
            if self.current_config.security_level < SecurityLevel.LEVEL_2:
                warnings.append("FIPS mode requires security level 2 or higher")

            disabled_fips_algs = {"MD5", "RC4", "DES", "3DES"}
            if not disabled_fips_algs.issubset(self.current_config.disabled_algorithms):
                warnings.append("FIPS mode requires disabling weak algorithms")

        # Check minimum key sizes
        if self.current_config.security_level >= SecurityLevel.LEVEL_2:
            if self.current_config.min_key_sizes["RSA"] < 2048:
                warnings.append("Security level 2+ requires RSA keys >= 2048 bits")
            if self.current_config.min_key_sizes["ECDSA"] < 256:
                warnings.append("Security level 2+ requires ECDSA keys >= 256 bits")

        # Check TLS versions
        if self.current_config.security_level >= SecurityLevel.LEVEL_2:
            if "TLSv1.0" in self.current_config.tls_versions or "TLSv1.1" in self.current_config.tls_versions:
                warnings.append("Security level 2+ should disable TLS 1.0 and 1.1")

        return warnings

    def export_configuration_profile(self, profile_name: str, output_dir: str = ".") -> None:
        """
        Export current configuration as a reusable profile.

        Args:
            profile_name: Name for the configuration profile
            output_dir: Directory to save the profile
        """
        profile_dir = Path(output_dir) / "crypto_profiles" / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)

        # Save configuration
        config_path = profile_dir / "crypto.conf"
        self.save_configuration(str(config_path))

        # Generate OpenSSL config
        openssl_config_path = profile_dir / "openssl.cnf"
        self.generate_openssl_config(str(openssl_config_path))

        # Create profile metadata
        metadata = {
            "name": profile_name,
            "security_level": self.current_config.security_level.value,
            "fips_enabled": self.current_config.fips_enabled,
            "cipher_suite_profile": self.current_config.cipher_suites.value,
            "created": Path.cwd().name,
            "description": f"Crypto configuration profile: {profile_name}"
        }

        metadata_path = profile_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            import json
            json.dump(metadata, f, indent=2)

        print(f"Configuration profile exported to: {profile_dir}")

    def load_configuration_profile(self, profile_path: str) -> None:
        """
        Load a configuration profile.

        Args:
            profile_path: Path to the configuration profile directory
        """
        profile_dir = Path(profile_path)

        if not profile_dir.exists():
            raise FileNotFoundError(f"Profile directory not found: {profile_path}")

        config_path = profile_dir / "crypto.conf"
        if config_path.exists():
            self.config_file = str(config_path)
            self.current_config = self._load_configuration()
            print(f"Configuration profile loaded: {profile_path}")
        else:
            raise FileNotFoundError(f"Configuration file not found in profile: {config_path}")

    def compare_configurations(self, other_config: 'CryptoConfiguration') -> Dict[str, Any]:
        """
        Compare current configuration with another configuration.

        Args:
            other_config: Configuration to compare against

        Returns:
            Dictionary containing differences
        """
        differences = {}

        # Compare security level
        if self.current_config.security_level != other_config.security_level:
            differences["security_level"] = {
                "current": self.current_config.security_level.value,
                "other": other_config.security_level.value
            }

        # Compare algorithm sets
        enabled_diff = self.current_config.enabled_algorithms.symmetric_difference(other_config.enabled_algorithms)
        if enabled_diff:
            differences["enabled_algorithms"] = {
                "added": list(other_config.enabled_algorithms - self.current_config.enabled_algorithms),
                "removed": list(self.current_config.enabled_algorithms - other_config.enabled_algorithms)
            }

        disabled_diff = self.current_config.disabled_algorithms.symmetric_difference(other_config.disabled_algorithms)
        if disabled_diff:
            differences["disabled_algorithms"] = {
                "added": list(other_config.disabled_algorithms - self.current_config.disabled_algorithms),
                "removed": list(self.current_config.disabled_algorithms - other_config.disabled_algorithms)
            }

        # Compare key sizes
        key_size_diffs = {}
        for alg in set(self.current_config.min_key_sizes.keys()) | set(other_config.min_key_sizes.keys()):
            current_size = self.current_config.min_key_sizes.get(alg)
            other_size = other_config.min_key_sizes.get(alg)
            if current_size != other_size:
                key_size_diffs[alg] = {"current": current_size, "other": other_size}

        if key_size_diffs:
            differences["min_key_sizes"] = key_size_diffs

        # Compare other settings
        if self.current_config.fips_enabled != other_config.fips_enabled:
            differences["fips_enabled"] = {
                "current": self.current_config.fips_enabled,
                "other": other_config.fips_enabled
            }

        if self.current_config.cipher_suites != other_config.cipher_suites:
            differences["cipher_suites"] = {
                "current": self.current_config.cipher_suites.value,
                "other": other_config.cipher_suites.value
            }

        return differences

    def get_security_recommendations(self) -> List[str]:
        """
        Get security recommendations based on current configuration.

        Returns:
            List of security recommendations
        """
        recommendations = []

        if self.current_config.security_level == SecurityLevel.LEVEL_0:
            recommendations.append("Consider upgrading to security level 1 for basic protection")

        if not self.current_config.fips_enabled and self.current_config.security_level >= SecurityLevel.LEVEL_2:
            recommendations.append("Consider enabling FIPS mode for enhanced compliance")

        weak_alg_enabled = self.current_config.disabled_algorithms & {"MD5", "RC4", "DES"}
        if weak_alg_enabled:
            recommendations.append(f"Consider disabling weak algorithms: {', '.join(weak_alg_enabled)}")

        if self.current_config.min_key_sizes["RSA"] < 3072:
            recommendations.append("Consider using RSA keys >= 3072 bits for future-proofing")

        old_tls = {"TLSv1.0", "TLSv1.1"} & self.current_config.tls_versions
        if old_tls:
            recommendations.append(f"Consider disabling outdated TLS versions: {', '.join(old_tls)}")

        return recommendations