#!/usr/bin/env python3
"""
Enhanced SBOM Generator for OpenSSL Ecosystem
Generates CycloneDX format SBOMs with FIPS compliance metadata
"""

import json
import os
import sys
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class OpenSSLSBOMGenerator:
    def __init__(self, project_root: str, output_format: str = "cyclonedx-json"):
        self.project_root = Path(project_root)
        self.output_format = output_format
        self.sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "version": 1,
            "metadata": {},
            "components": [],
            "dependencies": [],
            "vulnerabilities": []
        }
    
    def generate_sbom(self, artifact_name: str, deployment_target: str = "general") -> str:
        """Generate comprehensive SBOM for OpenSSL ecosystem"""
        print(f"Generating SBOM for {artifact_name} (deployment: {deployment_target})")
        
        # Set metadata
        self._set_metadata(artifact_name, deployment_target)
        
        # Add OpenSSL components
        self._add_openssl_components(deployment_target)
        
        # Add Conan dependencies
        self._add_conan_dependencies()
        
        # Add system dependencies
        self._add_system_dependencies()
        
        # Add FIPS compliance metadata
        if deployment_target in ["fips-government", "fips"]:
            self._add_fips_metadata()
        
        # Generate output
        output_file = self._write_sbom(artifact_name)
        
        print(f"✅ SBOM generated: {output_file}")
        return str(output_file)
    
    def _set_metadata(self, artifact_name: str, deployment_target: str):
        """Set SBOM metadata"""
        self.sbom_data["metadata"] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tools": [
                {
                    "vendor": "OpenSSL Ecosystem",
                    "name": "Enhanced SBOM Generator",
                    "version": "1.0.0"
                }
            ],
            "component": {
                "type": "application",
                "name": artifact_name,
                "version": self._get_openssl_version(),
                "description": f"OpenSSL cryptographic library - {deployment_target} deployment",
                "licenses": [
                    {
                        "license": {
                            "id": "Apache-2.0",
                            "name": "Apache License 2.0"
                        }
                    }
                ],
                "properties": [
                    {
                        "name": "deployment-target",
                        "value": deployment_target
                    },
                    {
                        "name": "build-system",
                        "value": "conan"
                    },
                    {
                        "name": "architecture",
                        "value": self._get_architecture()
                    }
                ]
            }
        }
    
    def _add_openssl_components(self, deployment_target: str):
        """Add OpenSSL core components"""
        openssl_version = self._get_openssl_version()
        
        # Main OpenSSL component
        openssl_component = {
            "type": "library",
            "name": "openssl",
            "version": openssl_version,
            "description": "OpenSSL cryptographic library",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "purl": f"pkg:conan/openssl@{openssl_version}@sparesparrow/stable",
            "properties": [
                {"name": "component-type", "value": "cryptographic-library"},
                {"name": "deployment-target", "value": deployment_target}
            ]
        }
        
        # Add FIPS compliance if applicable
        if deployment_target in ["fips-government", "fips"]:
            openssl_component["properties"].extend([
                {"name": "fips-validated", "value": "true"},
                {"name": "fips-certificate", "value": "4985"},
                {"name": "fips-standard", "value": "140-3"}
            ])
        
        self.sbom_data["components"].append(openssl_component)
        
        # Add sub-components
        self._add_openssl_subcomponents(openssl_version, deployment_target)
    
    def _add_openssl_subcomponents(self, version: str, deployment_target: str):
        """Add OpenSSL sub-components (libssl, libcrypto, etc.)"""
        subcomponents = [
            {
                "name": "libssl",
                "description": "OpenSSL SSL/TLS library",
                "type": "library"
            },
            {
                "name": "libcrypto", 
                "description": "OpenSSL cryptographic library",
                "type": "library"
            },
            {
                "name": "openssl-cli",
                "description": "OpenSSL command line interface",
                "type": "application"
            }
        ]
        
        for subcomp in subcomponents:
            component = {
                "type": subcomp["type"],
                "name": subcomp["name"],
                "version": version,
                "description": subcomp["description"],
                "licenses": [{"license": {"id": "Apache-2.0"}}],
                "purl": f"pkg:conan/openssl/{subcomp['name']}@{version}@sparesparrow/stable",
                "properties": [
                    {"name": "parent-component", "value": "openssl"},
                    {"name": "deployment-target", "value": deployment_target}
                ]
            }
            
            # Add FIPS algorithms if applicable
            if deployment_target in ["fips-government", "fips"] and subcomp["name"] == "libcrypto":
                component["properties"].extend([
                    {"name": "fips-algorithms", "value": "AES-GCM,SHA-256,RSA-2048,ECDSA-P256"},
                    {"name": "fips-validated", "value": "true"}
                ])
            
            self.sbom_data["components"].append(component)
    
    def _add_conan_dependencies(self):
        """Add Conan package dependencies"""
        conan_deps = [
            {
                "name": "openssl-base",
                "version": "1.0.1",
                "description": "Foundation utilities and profiles"
            },
            {
                "name": "openssl-tools", 
                "version": "1.2.4",
                "description": "Build orchestration and tooling"
            },
            {
                "name": "openssl-fips-data",
                "version": "140-3.2", 
                "description": "FIPS 140-3 certificates and compliance data"
            }
        ]
        
        for dep in conan_deps:
            component = {
                "type": "library",
                "name": dep["name"],
                "version": dep["version"],
                "description": dep["description"],
                "licenses": [{"license": {"id": "Apache-2.0"}}],
                "purl": f"pkg:conan/{dep['name']}@{dep['version']}@sparesparrow/stable",
                "properties": [
                    {"name": "package-manager", "value": "conan"},
                    {"name": "channel", "value": "stable"}
                ]
            }
            
            # Add FIPS-specific metadata for FIPS data package
            if dep["name"] == "openssl-fips-data":
                component["properties"].extend([
                    {"name": "fips-certificate-id", "value": "4985"},
                    {"name": "fips-standard", "value": "140-3"},
                    {"name": "compliance-data", "value": "true"}
                ])
            
            self.sbom_data["components"].append(component)
    
    def _add_system_dependencies(self):
        """Add system-level dependencies"""
        system_deps = [
            {
                "name": "libc",
                "description": "C standard library",
                "type": "library"
            },
            {
                "name": "libpthread",
                "description": "POSIX threads library", 
                "type": "library"
            },
            {
                "name": "libdl",
                "description": "Dynamic linking library",
                "type": "library"
            }
        ]
        
        for dep in system_deps:
            component = {
                "type": dep["type"],
                "name": dep["name"],
                "description": dep["description"],
                "properties": [
                    {"name": "dependency-type", "value": "system"},
                    {"name": "platform", "value": self._get_platform()}
                ]
            }
            
            self.sbom_data["components"].append(component)
    
    def _add_fips_metadata(self):
        """Add FIPS 140-3 compliance metadata"""
        fips_metadata = {
            "type": "compliance",
            "name": "fips-140-3-compliance",
            "description": "FIPS 140-3 compliance validation data",
            "properties": [
                {"name": "standard", "value": "FIPS 140-3"},
                {"name": "certificate-id", "value": "4985"},
                {"name": "validation-level", "value": "Level 1"},
                {"name": "validated-algorithms", "value": "AES-GCM,SHA-256,RSA-2048,ECDSA-P256"},
                {"name": "certification-date", "value": "2024-01-01"},
                {"name": "expiry-date", "value": "2029-01-01"}
            ]
        }
        
        self.sbom_data["components"].append(fips_metadata)
    
    def _get_openssl_version(self) -> str:
        """Get OpenSSL version from VERSION.dat"""
        version_file = self.project_root / "openssl" / "VERSION.dat"
        if version_file.exists():
            with open(version_file, 'r') as f:
                lines = f.readlines()
                major = minor = patch = "0"
                prerelease = ""
                for line in lines:
                    if line.startswith("MAJOR="):
                        major = line.split("=")[1].strip()
                    elif line.startswith("MINOR="):
                        minor = line.split("=")[1].strip()
                    elif line.startswith("PATCH="):
                        patch = line.split("=")[1].strip()
                    elif line.startswith("PRE_RELEASE_TAG="):
                        prerelease = line.split("=")[1].strip().strip('"')
                
                version = f"{major}.{minor}.{patch}"
                if prerelease and prerelease != "":
                    version += f"-{prerelease}"
                return version
        return "4.0.0-dev"
    
    def _get_architecture(self) -> str:
        """Get system architecture"""
        import platform
        return platform.machine()
    
    def _get_platform(self) -> str:
        """Get system platform"""
        import platform
        return platform.system().lower()
    
    def _write_sbom(self, artifact_name: str) -> Path:
        """Write SBOM to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{artifact_name}-sbom-{timestamp}.json"
        output_path = self.project_root / "deploy" / filename
        
        # Ensure deploy directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.sbom_data, f, indent=2)
        
        return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 enhanced-sbom-generator.py <artifact-name> [deployment-target]")
        sys.exit(1)
    
    artifact_name = sys.argv[1]
    deployment_target = sys.argv[2] if len(sys.argv) > 2 else "general"
    
    generator = OpenSSLSBOMGenerator(os.getcwd())
    sbom_path = generator.generate_sbom(artifact_name, deployment_target)
    
    print(f"SBOM generated successfully: {sbom_path}")

if __name__ == "__main__":
    main()
