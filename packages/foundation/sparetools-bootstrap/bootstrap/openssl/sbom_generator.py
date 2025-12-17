#!/usr/bin/env python3
"""
Software Bill of Materials (SBOM) Generator for OpenSSL

This module generates comprehensive SBOMs for OpenSSL builds in multiple formats
including SPDX, CycloneDX, and custom formats.
"""

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SBOMFormat(Enum):
    """Supported SBOM formats."""
    SPDX = "spdx"
    CYCLONEDX = "cyclonedx"
    CUSTOM = "custom"


class ComponentType(Enum):
    """Types of software components."""
    LIBRARY = "library"
    APPLICATION = "application"
    FRAMEWORK = "framework"
    OPERATING_SYSTEM = "operating-system"
    CONTAINER = "container"
    FIRMWARE = "firmware"


class LicenseType(Enum):
    """License types for components."""
    APACHE_2_0 = "Apache-2.0"
    BSD_3_CLAUSE = "BSD-3-Clause"
    MIT = "MIT"
    OPENSSL = "OpenSSL"
    CUSTOM = "custom"


@dataclass
class SBOMComponent:
    """Represents a component in the SBOM."""
    name: str
    version: str
    component_type: ComponentType
    license: LicenseType
    supplier: Optional[str] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    download_location: Optional[str] = None
    hash_algorithm: str = "SHA256"
    hash_value: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_hash(self, file_path: Optional[str] = None, data: Optional[bytes] = None) -> None:
        """Calculate hash for the component."""
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()

        if data:
            self.hash_value = hashlib.sha256(data).hexdigest()


@dataclass
class SBOMDocument:
    """Complete SBOM document."""
    format: SBOMFormat
    version: str
    name: str
    namespace: str
    creation_timestamp: str
    creators: List[str]
    components: List[SBOMComponent]
    relationships: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.now().isoformat()


class SBOMGenerator:
    """
    Software Bill of Materials generator for OpenSSL.

    This class analyzes OpenSSL builds and generates comprehensive SBOMs
    that document all components, dependencies, and build artifacts.
    """

    # Known OpenSSL dependencies and their metadata
    KNOWN_DEPENDENCIES = {
        "zlib": {
            "version": "1.2.11",
            "license": LicenseType.CUSTOM,
            "supplier": "Jean-loup Gailly and Mark Adler",
            "description": "A massively spiffy yet delicately unobtrusive compression library"
        },
        "perl": {
            "version": "5.30.0",
            "license": LicenseType.CUSTOM,
            "supplier": "Perl Foundation",
            "description": "Perl programming language"
        },
        "make": {
            "version": "4.3",
            "license": LicenseType.APACHE_2_0,
            "supplier": "GNU Project",
            "description": "GNU Make build tool"
        }
    }

    def __init__(self, openssl_source_path: Optional[str] = None, build_path: Optional[str] = None):
        """
        Initialize the SBOM generator.

        Args:
            openssl_source_path: Path to OpenSSL source directory
            build_path: Path to OpenSSL build directory
        """
        self.openssl_source = Path(openssl_source_path) if openssl_source_path else None
        self.build_path = Path(build_path) if build_path else None
        self.components_cache: Dict[str, SBOMComponent] = {}

    def generate_sbom(self,
                     format_type: SBOMFormat = SBOMFormat.SPDX,
                     openssl_version: str = "3.1.0",
                     include_build_artifacts: bool = True) -> SBOMDocument:
        """
        Generate a comprehensive SBOM for OpenSSL.

        Args:
            format_type: SBOM format to generate
            openssl_version: OpenSSL version being documented
            include_build_artifacts: Whether to include build artifacts

        Returns:
            Complete SBOM document
        """
        # Create main OpenSSL component
        openssl_component = self._create_openssl_component(openssl_version)

        components = [openssl_component]
        relationships = []

        # Add dependencies
        dependencies = self._analyze_dependencies()
        for dep in dependencies:
            components.append(dep)
            relationships.append({
                "source": openssl_component.name,
                "target": dep.name,
                "relationship": "DEPENDS_ON"
            })

        # Add build artifacts if requested
        if include_build_artifacts and self.build_path:
            build_artifacts = self._analyze_build_artifacts()
            for artifact in build_artifacts:
                components.append(artifact)
                relationships.append({
                    "source": openssl_component.name,
                    "target": artifact.name,
                    "relationship": "BUILD_ARTIFACT"
                })

        # Create SBOM document
        document = SBOMDocument(
            format=format_type,
            version="1.0",
            name=f"OpenSSL-{openssl_version}-SBOM",
            namespace=f"urn:openssl:{openssl_version}:sbom",
            creation_timestamp=datetime.now().isoformat(),
            creators=["OpenSSL SBOM Generator"],
            components=components,
            relationships=relationships,
            metadata={
                "tool_name": "shared-dev-tools SBOM Generator",
                "tool_version": "1.0.0",
                "openssl_version": openssl_version,
                "generation_date": datetime.now().isoformat()
            }
        )

        return document

    def _create_openssl_component(self, version: str) -> SBOMComponent:
        """Create the main OpenSSL component."""
        component = SBOMComponent(
            name="OpenSSL",
            version=version,
            component_type=ComponentType.LIBRARY,
            license=LicenseType.OPENSSL,
            supplier="OpenSSL Software Foundation",
            description="Cryptography and SSL/TLS Toolkit",
            homepage="https://www.openssl.org/",
            download_location="https://www.openssl.org/source/"
        )

        # Calculate hash if source is available
        if self.openssl_source:
            tarball_path = self._find_openssl_tarball()
            if tarball_path:
                component.calculate_hash(tarball_path)

        return component

    def _find_openssl_tarball(self) -> Optional[str]:
        """Find OpenSSL source tarball."""
        if not self.openssl_source:
            return None

        # Look for tar.gz files in source directory
        for file in self.openssl_source.glob("*.tar.gz"):
            return str(file)

        return None

    def _analyze_dependencies(self) -> List[SBOMComponent]:
        """Analyze OpenSSL build dependencies."""
        components = []

        # Check for common build dependencies
        if self.openssl_source:
            # Check Makefile or configure script for dependencies
            makefile_path = self.openssl_source / "Makefile"
            if makefile_path.exists():
                deps = self._parse_makefile_dependencies(makefile_path)
                for dep_name in deps:
                    if dep_name in self.KNOWN_DEPENDENCIES:
                        dep_info = self.KNOWN_DEPENDENCIES[dep_name]
                        component = SBOMComponent(
                            name=dep_name,
                            version=dep_info["version"],
                            component_type=ComponentType.LIBRARY,
                            license=dep_info["license"],
                            supplier=dep_info["supplier"],
                            description=dep_info["description"]
                        )
                        components.append(component)

        # Add standard dependencies that are typically required
        standard_deps = ["zlib", "perl"]
        for dep in standard_deps:
            if dep in self.KNOWN_DEPENDENCIES and not any(c.name == dep for c in components):
                dep_info = self.KNOWN_DEPENDENCIES[dep]
                component = SBOMComponent(
                    name=dep,
                    version=dep_info["version"],
                    component_type=ComponentType.LIBRARY,
                    license=dep_info["license"],
                    supplier=dep_info["supplier"],
                    description=dep_info["description"]
                )
                components.append(component)

        return components

    def _parse_makefile_dependencies(self, makefile_path: Path) -> Set[str]:
        """Parse Makefile to extract dependencies."""
        dependencies = set()

        try:
            with open(makefile_path, 'r') as f:
                content = f.read()

            # Look for common dependency patterns
            dep_patterns = [
                r'LIBS\s*=\s*(.*)',
                r'DEPENDS\s*=\s*(.*)',
                r'LDFLAGS\s*=\s*-l(\w+)',
                r'PKG_CONFIG\s*=\s*(.*)'
            ]

            for pattern in dep_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Extract library names from -l flags
                    if match.startswith('-l'):
                        lib_name = match[2:].split()[0]
                        dependencies.add(lib_name)
                    else:
                        # Split on common separators and add
                        parts = re.split(r'[,\s]+', match)
                        for part in parts:
                            if part and not part.startswith('-'):
                                dependencies.add(part.strip())

        except Exception as e:
            print(f"Warning: Could not parse Makefile dependencies: {e}")

        return dependencies

    def _analyze_build_artifacts(self) -> List[SBOMComponent]:
        """Analyze build artifacts for inclusion in SBOM."""
        components = []

        if not self.build_path or not self.build_path.exists():
            return components

        # Common OpenSSL build artifacts
        artifact_patterns = [
            ("libcrypto.so*", ComponentType.LIBRARY, "OpenSSL cryptography library"),
            ("libssl.so*", ComponentType.LIBRARY, "OpenSSL SSL/TLS library"),
            ("openssl", ComponentType.APPLICATION, "OpenSSL command-line tool"),
            ("fips.so*", ComponentType.LIBRARY, "OpenSSL FIPS module"),
            ("engines/*.so", ComponentType.LIBRARY, "OpenSSL engine modules")
        ]

        for pattern, comp_type, description in artifact_patterns:
            for file_path in self.build_path.glob(pattern):
                if file_path.is_file():
                    component = SBOMComponent(
                        name=file_path.name,
                        version=self._get_file_version(file_path),
                        component_type=comp_type,
                        license=LicenseType.OPENSSL,
                        supplier="OpenSSL Software Foundation",
                        description=description
                    )
                    component.calculate_hash(str(file_path))
                    components.append(component)

        return components

    def _get_file_version(self, file_path: Path) -> str:
        """Extract version information from a file."""
        try:
            # Try to get version from file metadata or content
            result = subprocess.run(['file', str(file_path)],
                                  capture_output=True,
                                  text=True,
                                  timeout=10)

            if result.returncode == 0:
                # Look for version patterns in file output
                version_match = re.search(r'version\s+([\d.]+)', result.stdout, re.IGNORECASE)
                if version_match:
                    return version_match.group(1)

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass

        # Return unknown if we can't determine version
        return "unknown"

    def export_sbom(self, document: SBOMDocument, output_path: str) -> None:
        """
        Export SBOM document to file.

        Args:
            document: SBOM document to export
            output_path: Path to save the SBOM
        """
        if document.format == SBOMFormat.SPDX:
            self._export_spdx(document, output_path)
        elif document.format == SBOMFormat.CYCLONEDX:
            self._export_cyclonedx(document, output_path)
        else:
            self._export_custom(document, output_path)

        print(f"SBOM exported to: {output_path}")

    def _export_spdx(self, document: SBOMDocument, output_path: str) -> None:
        """Export SBOM in SPDX format."""
        spdx_data = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": f"SPDXRef-DOCUMENT-{document.name}",
            "documentName": document.name,
            "documentNamespace": document.namespace,
            "creationInfo": {
                "created": document.creation_timestamp,
                "creators": document.creators
            },
            "packages": []
        }

        for component in document.components:
            package = {
                "SPDXID": f"SPDXRef-Package-{component.name}",
                "name": component.name,
                "versionInfo": component.version,
                "downloadLocation": component.download_location or "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "licenseConcluded": component.license.value,
                "supplier": f"Organization: {component.supplier}" if component.supplier else "NOASSERTION",
                "packageVerificationCode": {
                    "packageVerificationCodeValue": component.hash_value or "NOASSERTION"
                }
            }

            if component.description:
                package["description"] = component.description

            spdx_data["packages"].append(package)

        with open(output_path, 'w') as f:
            json.dump(spdx_data, f, indent=2)

    def _export_cyclonedx(self, document: SBOMDocument, output_path: str) -> None:
        """Export SBOM in CycloneDX format."""
        cyclonedx_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "serialNumber": f"urn:uuid:{document.namespace}",
            "version": 1,
            "metadata": {
                "timestamp": document.creation_timestamp,
                "tools": [{
                    "vendor": "shared-dev-tools",
                    "name": "SBOM Generator",
                    "version": "1.0.0"
                }],
                "component": {
                    "type": "library",
                    "name": document.name,
                    "version": document.version
                }
            },
            "components": []
        }

        for component in document.components:
            comp_data = {
                "type": component.component_type.value,
                "name": component.name,
                "version": component.version,
                "licenses": [{
                    "license": {
                        "id": component.license.value
                    }
                }]
            }

            if component.supplier:
                comp_data["supplier"] = {"name": component.supplier}

            if component.description:
                comp_data["description"] = component.description

            if component.hash_value:
                comp_data["hashes"] = [{
                    "alg": component.hash_algorithm,
                    "content": component.hash_value
                }]

            cyclonedx_data["components"].append(comp_data)

        with open(output_path, 'w') as f:
            json.dump(cyclonedx_data, f, indent=2)

    def _export_custom(self, document: SBOMDocument, output_path: str) -> None:
        """Export SBOM in custom format."""
        custom_data = document.__dict__.copy()

        # Convert enums to values
        custom_data["format"] = document.format.value
        custom_data["components"] = [comp.__dict__ for comp in document.components]

        for comp in custom_data["components"]:
            comp["component_type"] = comp["component_type"].value
            comp["license"] = comp["license"].value

        with open(output_path, 'w') as f:
            json.dump(custom_data, f, indent=2)

    def validate_sbom(self, sbom_path: str) -> List[str]:
        """
        Validate an SBOM file for completeness and correctness.

        Args:
            sbom_path: Path to SBOM file to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            with open(sbom_path, 'r') as f:
                data = json.load(f)

            # Basic structure validation
            required_fields = ["format", "version", "name", "components"]
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")

            if "components" in data:
                components = data["components"]
                if not isinstance(components, list):
                    errors.append("Components must be a list")
                else:
                    for i, comp in enumerate(components):
                        comp_errors = self._validate_component(comp, i)
                        errors.extend(comp_errors)

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {e}")
        except Exception as e:
            errors.append(f"Validation error: {e}")

        return errors

    def _validate_component(self, component: Dict[str, Any], index: int) -> List[str]:
        """Validate a single component."""
        errors = []

        required_comp_fields = ["name", "version", "component_type", "license"]
        for field in required_comp_fields:
            if field not in component:
                errors.append(f"Component {index}: Missing required field '{field}'")

        # Validate license
        if "license" in component:
            license_value = component["license"]
            valid_licenses = [lt.value for lt in LicenseType]
            if license_value not in valid_licenses:
                errors.append(f"Component {index}: Invalid license '{license_value}'")

        return errors

    def merge_sboms(self, sbom_paths: List[str], output_path: str) -> None:
        """
        Merge multiple SBOM files into a single comprehensive SBOM.

        Args:
            sbom_paths: List of SBOM file paths to merge
            output_path: Path to save the merged SBOM
        """
        merged_components = []
        merged_relationships = []
        seen_components = set()

        for sbom_path in sbom_paths:
            try:
                with open(sbom_path, 'r') as f:
                    sbom_data = json.load(f)

                # Extract components
                if "components" in sbom_data:
                    for comp in sbom_data["components"]:
                        comp_key = f"{comp['name']}:{comp['version']}"
                        if comp_key not in seen_components:
                            merged_components.append(comp)
                            seen_components.add(comp_key)

                # Extract relationships if available
                if "relationships" in sbom_data:
                    merged_relationships.extend(sbom_data["relationships"])

            except Exception as e:
                print(f"Warning: Could not process SBOM {sbom_path}: {e}")

        # Create merged SBOM
        merged_sbom = {
            "format": "custom",
            "version": "1.0",
            "name": "Merged-OpenSSL-SBOM",
            "namespace": f"urn:merged-openssl:sbom:{datetime.now().isoformat()}",
            "creation_timestamp": datetime.now().isoformat(),
            "creators": ["OpenSSL SBOM Merger"],
            "components": merged_components,
            "relationships": merged_relationships,
            "metadata": {
                "merged_from": sbom_paths,
                "merge_timestamp": datetime.now().isoformat()
            }
        }

        with open(output_path, 'w') as f:
            json.dump(merged_sbom, f, indent=2)

        print(f"Merged SBOM saved to: {output_path}")
        print(f"Total components: {len(merged_components)}")
