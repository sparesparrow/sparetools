"""Provider dependency ordering logic for OpenSSL 3.6+."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

LOG = logging.getLogger(__name__)


class ProviderType(Enum):
    """OpenSSL provider types."""
    BASE = "base"           # Base provider (internal abstractions)
    DEFAULT = "default"     # Default provider (core algorithms)
    LEGACY = "legacy"       # Legacy provider (deprecated algorithms)
    FIPS = "fips"          # FIPS provider (FIPS 140-3 module)
    NULL = "null"          # Null provider (testing)


@dataclass
class ProviderInfo:
    """Information about an OpenSSL provider."""
    name: str
    provider_type: ProviderType
    dependencies: Set[str]
    source_files: List[str]
    requires_crypto: bool = True
    optional: bool = False
    openssl_version_min: str = "3.0.0"


# Provider dependency graph for OpenSSL 3.6+
PROVIDER_GRAPH = {
    "base": ProviderInfo(
        name="base",
        provider_type=ProviderType.BASE,
        dependencies=set(),
        source_files=[
            "providers/baseprov.c",
            "providers/common/bio_prov.c",
            "providers/common/capabilities.c",
        ],
        requires_crypto=True,
        optional=False,
        openssl_version_min="3.0.0"
    ),
    "default": ProviderInfo(
        name="default",
        provider_type=ProviderType.DEFAULT,
        dependencies={"base"},
        source_files=[
            "providers/defltprov.c",
            "providers/implementations/ciphers/*.c",
            "providers/implementations/digests/*.c",
            "providers/implementations/kdfs/*.c",
            "providers/implementations/macs/*.c",
            "providers/implementations/keymgmt/*.c",
            "providers/implementations/signature/*.c",
            "providers/implementations/asymciphers/*.c",
            "providers/implementations/kem/*.c",
            "providers/implementations/exchange/*.c",
            "providers/implementations/rands/*.c",
        ],
        requires_crypto=True,
        optional=False,
        openssl_version_min="3.0.0"
    ),
    "legacy": ProviderInfo(
        name="legacy",
        provider_type=ProviderType.LEGACY,
        dependencies={"base", "default"},
        source_files=[
            "providers/legacyprov.c",
            "providers/implementations/digests/md2_prov.c",
            "providers/implementations/digests/md4_prov.c",
            "providers/implementations/digests/mdc2_prov.c",
            "providers/implementations/digests/wp_prov.c",
            "providers/implementations/ciphers/cipher_des*.c",
            "providers/implementations/ciphers/cipher_blowfish*.c",
            "providers/implementations/ciphers/cipher_cast*.c",
            "providers/implementations/ciphers/cipher_rc2*.c",
            "providers/implementations/ciphers/cipher_rc4*.c",
            "providers/implementations/ciphers/cipher_rc5*.c",
            "providers/implementations/ciphers/cipher_idea*.c",
            "providers/implementations/ciphers/cipher_seed*.c",
        ],
        requires_crypto=True,
        optional=True,
        openssl_version_min="3.0.0"
    ),
    "fips": ProviderInfo(
        name="fips",
        provider_type=ProviderType.FIPS,
        dependencies={"base"},
        source_files=[
            "providers/fipsprov.c",
            "providers/fips/*.c",
            "providers/implementations/ciphers/cipher_aes*.c",
            "providers/implementations/digests/sha2_prov.c",
            "providers/implementations/digests/sha3_prov.c",
            "providers/implementations/macs/hmac_prov.c",
            "providers/implementations/macs/cmac_prov.c",
            "providers/implementations/kdfs/kbkdf.c",
            "providers/implementations/kdfs/pbkdf2.c",
        ],
        requires_crypto=True,
        optional=True,
        openssl_version_min="3.0.0"
    ),
    "null": ProviderInfo(
        name="null",
        provider_type=ProviderType.NULL,
        dependencies=set(),
        source_files=[
            "providers/nullprov.c",
        ],
        requires_crypto=False,
        optional=True,
        openssl_version_min="3.0.0"
    ),
}


class ProviderOrderer:
    """Determines optimal build order for OpenSSL providers."""

    def __init__(
        self,
        openssl_version: str = "3.6.0",
        enable_fips: bool = False,
        enable_legacy: bool = False,
        excluded_algorithms: Optional[Set[str]] = None
    ):
        """Initialize provider orderer.
        
        Args:
            openssl_version: OpenSSL version (e.g., "3.6.0")
            enable_fips: Whether to include FIPS provider
            enable_legacy: Whether to include legacy provider
            excluded_algorithms: Set of algorithms to exclude (e.g., {"md2", "md4", "rc5"})
        """
        self.openssl_version = openssl_version
        self.enable_fips = enable_fips
        self.enable_legacy = enable_legacy
        self.excluded_algorithms = excluded_algorithms or set()
        
        self._build_order: Optional[List[str]] = None
        self._filtered_sources: Optional[Dict[str, List[str]]] = None

    def get_build_order(self) -> List[str]:
        """Get provider build order using topological sort.
        
        Returns:
            List of provider names in build order
        """
        if self._build_order is not None:
            return self._build_order

        # Determine which providers to include
        providers_to_build = {"base", "default"}  # Always required
        
        if self.enable_fips:
            providers_to_build.add("fips")
        
        if self.enable_legacy:
            providers_to_build.add("legacy")

        # Topological sort with dependency resolution
        build_order = []
        visited = set()
        temp_visited = set()

        def visit(provider_name: str):
            if provider_name in temp_visited:
                raise RuntimeError(f"Circular dependency detected: {provider_name}")
            if provider_name in visited:
                return

            temp_visited.add(provider_name)
            
            provider = PROVIDER_GRAPH.get(provider_name)
            if not provider:
                LOG.warning(f"Unknown provider: {provider_name}")
                return

            # Visit dependencies first
            for dep in provider.dependencies:
                if dep in providers_to_build:
                    visit(dep)

            temp_visited.remove(provider_name)
            visited.add(provider_name)
            build_order.append(provider_name)

        # Visit all selected providers
        for provider_name in providers_to_build:
            if provider_name not in visited:
                visit(provider_name)

        self._build_order = build_order
        LOG.info(f"Provider build order: {' -> '.join(build_order)}")
        return build_order

    def get_filtered_sources(self, provider_name: str) -> List[str]:
        """Get filtered source files for a provider.
        
        Filters out sources based on excluded algorithms.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            List of source file patterns
        """
        provider = PROVIDER_GRAPH.get(provider_name)
        if not provider:
            return []

        filtered = []
        for source in provider.source_files:
            # Check if source should be excluded based on algorithm
            exclude = False
            for algo in self.excluded_algorithms:
                algo_lower = algo.lower()
                if algo_lower in source.lower():
                    LOG.info(f"Excluding {source} (algorithm: {algo})")
                    exclude = True
                    break
            
            if not exclude:
                filtered.append(source)

        return filtered

    def get_make_dependencies(self) -> str:
        """Generate Makefile dependencies for providers.
        
        Returns:
            Makefile fragment with provider dependencies
        """
        build_order = self.get_build_order()
        
        makefile_lines = [
            "# Provider build order and dependencies",
            "# Generated by provider_ordering.py",
            ""
        ]

        for i, provider in enumerate(build_order):
            provider_info = PROVIDER_GRAPH[provider]
            
            # Build target name
            target = f"provider_{provider}"
            
            # Dependencies
            deps = []
            if provider_info.requires_crypto:
                deps.append("libcrypto.a")
            
            # Add provider dependencies
            for dep in provider_info.dependencies:
                if dep in build_order:
                    deps.append(f"provider_{dep}")
            
            deps_str = " ".join(deps) if deps else ""
            
            makefile_lines.append(f"{target}: {deps_str}")
            
            # Source files
            sources = self.get_filtered_sources(provider)
            if sources:
                makefile_lines.append(f"\t# Build {provider} provider")
                for source in sources[:3]:  # Show first 3 as examples
                    makefile_lines.append(f"\t# Source: {source}")
                if len(sources) > 3:
                    makefile_lines.append(f"\t# ... and {len(sources) - 3} more files")
            makefile_lines.append("")

        # All providers target
        all_providers = " ".join(f"provider_{p}" for p in build_order)
        makefile_lines.extend([
            "# Build all providers in correct order",
            f"providers: {all_providers}",
            "",
            ".PHONY: providers " + " ".join(f"provider_{p}" for p in build_order)
        ])

        return "\n".join(makefile_lines)

    def validate_provider_availability(self, openssl_source_dir: str) -> Dict[str, bool]:
        """Validate which providers are available in the OpenSSL source.
        
        Args:
            openssl_source_dir: Path to OpenSSL source directory
            
        Returns:
            Dictionary mapping provider names to availability status
        """
        import os
        from pathlib import Path

        source_path = Path(openssl_source_dir)
        availability = {}

        for provider_name, provider_info in PROVIDER_GRAPH.items():
            # Check if at least one source file exists
            available = False
            for source_pattern in provider_info.source_files[:5]:  # Check first 5
                # Remove wildcards for existence check
                source_file = source_pattern.replace("*.c", "").replace("/*", "")
                if source_file.endswith("/"):
                    # Check directory
                    if (source_path / source_file).is_dir():
                        available = True
                        break
                else:
                    # Check file
                    if (source_path / source_file).exists():
                        available = True
                        break
            
            availability[provider_name] = available
            
            if not available and not provider_info.optional:
                LOG.warning(
                    f"Required provider '{provider_name}' sources not found in {openssl_source_dir}"
                )

        return availability


def get_provider_exclusions_for_version(version: str) -> Set[str]:
    """Get recommended algorithm exclusions for OpenSSL version.
    
    Args:
        version: OpenSSL version string (e.g., "3.6.0")
        
    Returns:
        Set of algorithms to exclude
    """
    major, minor, patch = [int(x) for x in version.split(".")[:3]]
    
    exclusions = set()
    
    # MD2 and MD4 are deprecated in all 3.x versions
    exclusions.update({"md2", "md4"})
    
    # RC5 is patented
    exclusions.add("rc5")
    
    # For OpenSSL 3.6+, exclude problematic LMS provider
    if major == 3 and minor >= 6:
        exclusions.add("lms")
        LOG.info("Excluding LMS provider for OpenSSL 3.6+ (known compilation issues)")
    
    # FIPS-related exclusions for non-FIPS builds
    # These will be handled separately in FIPS-enabled builds
    
    return exclusions


def generate_provider_makefile_fragment(
    openssl_version: str = "3.6.0",
    enable_fips: bool = False,
    enable_legacy: bool = False,
    output_file: Optional[str] = None
) -> str:
    """Generate Makefile fragment with provider dependencies.
    
    Args:
        openssl_version: OpenSSL version
        enable_fips: Enable FIPS provider
        enable_legacy: Enable legacy provider  
        output_file: Optional output file path
        
    Returns:
        Makefile fragment as string
    """
    exclusions = get_provider_exclusions_for_version(openssl_version)
    
    orderer = ProviderOrderer(
        openssl_version=openssl_version,
        enable_fips=enable_fips,
        enable_legacy=enable_legacy,
        excluded_algorithms=exclusions
    )
    
    makefile_content = orderer.get_make_dependencies()
    
    if output_file:
        with open(output_file, "w") as f:
            f.write(makefile_content)
        LOG.info(f"Provider Makefile fragment written to {output_file}")
    
    return makefile_content


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    print("=== Provider Build Order for OpenSSL 3.6.0 ===\n")
    
    # Standard build
    print("Standard build (no FIPS, no legacy):")
    orderer = ProviderOrderer(openssl_version="3.6.0")
    print(f"  Order: {' -> '.join(orderer.get_build_order())}\n")
    
    # FIPS build
    print("FIPS build:")
    orderer_fips = ProviderOrderer(openssl_version="3.6.0", enable_fips=True)
    print(f"  Order: {' -> '.join(orderer_fips.get_build_order())}\n")
    
    # Full build
    print("Full build (with legacy):")
    orderer_full = ProviderOrderer(openssl_version="3.6.0", enable_fips=True, enable_legacy=True)
    print(f"  Order: {' -> '.join(orderer_full.get_build_order())}\n")
    
    # Generate Makefile fragment
    print("=== Makefile Fragment ===\n")
    makefile = generate_provider_makefile_fragment(openssl_version="3.6.0", enable_fips=True)
    print(makefile)

