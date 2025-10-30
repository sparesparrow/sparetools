import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict

def generate_openssl_sbom(
    package_name: str,
    version: str,
    is_fips: bool = False,
    fips_cert: Optional[str] = None,
    dependencies: Optional[List[Dict]] = None,
    output_path: Optional[Path] = None,
) -> dict:
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "component": {
                "type": "library",
                "name": package_name,
                "version": version,
                "purl": f"pkg:conan/{package_name}@{version}",
                "properties": [],
            }
        },
        "components": dependencies or [],
    }
    if is_fips and fips_cert:
        sbom["metadata"]["component"]["properties"].extend(
            [
                {"name": "openssl:fips_validated", "value": "true"},
                {"name": "openssl:fips_certificate", "value": fips_cert},
                {"name": "openssl:deployment_target", "value": "government"},
                {"name": "openssl:compliance_standard", "value": "FIPS 140-3"},
            ]
        )
    if output_path:
        output_path.write_text(json.dumps(sbom, indent=2))
    return sbom
