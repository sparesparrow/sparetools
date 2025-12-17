#!/usr/bin/env python3
"""
Artifact Uploader for SpareTools CI/CD

Handles uploading build artifacts to various destinations:
- Cloudsmith (primary package registry)
- GitHub Packages
- Local artifact storage
- SBOM repositories
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from recipe_base import load_consumer_config


class ArtifactUploader:
    """Handles uploading build artifacts to various destinations."""

    def __init__(self, target: str = "cloudsmith", api_key: Optional[str] = None,
                 dry_run: bool = False, verbose: bool = False):
        """Initialize artifact uploader.

        Args:
            target: Upload target ('cloudsmith', 'github', 'local')
            api_key: API key for target registry
            dry_run: If True, only simulate uploads
            verbose: Enable verbose output
        """
        self.target = target
        self.api_key = api_key or os.environ.get("CLOUDSMITH_API_KEY")
        self.dry_run = dry_run
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Log a message if verbose."""
        if self.verbose:
            print(f"[UPLOAD] {message}")

    def upload_package(self, package_name: str, version: str,
                      package_path: Optional[str] = None,
                      consumer: Optional[str] = None) -> bool:
        """Upload a single package.

        Args:
            package_name: Name of package to upload
            version: Package version
            package_path: Path to package file (if None, find automatically)
            consumer: Consumer domain (for metadata)

        Returns:
            True if upload successful
        """
        if self.target == "cloudsmith":
            return self._upload_to_cloudsmith(package_name, version, package_path, consumer)
        elif self.target == "github":
            return self._upload_to_github(package_name, version, package_path, consumer)
        elif self.target == "local":
            return self._upload_to_local(package_name, version, package_path, consumer)
        else:
            print(f"Unsupported target: {self.target}")
            return False

    def upload_artifacts(self, artifacts_dir: str, consumer: Optional[str] = None) -> Dict[str, Any]:
        """Upload all artifacts from a directory.

        Args:
            artifacts_dir: Directory containing artifacts
            consumer: Consumer domain

        Returns:
            Upload results dictionary
        """
        results = {
            "uploaded": [],
            "failed": [],
            "skipped": [],
            "total": 0
        }

        artifacts_path = Path(artifacts_dir)
        if not artifacts_path.exists():
            self.log(f"Artifacts directory not found: {artifacts_dir}")
            return results

        # Find all package files
        package_extensions = [".tar.gz", ".zip", ".deb", ".rpm", ".pkg"]

        for item in artifacts_path.rglob("*"):
            if item.is_file():
                for ext in package_extensions:
                    if item.name.endswith(ext):
                        results["total"] += 1

                        # Extract package info from filename
                        package_info = self._parse_package_filename(item.name)
                        if not package_info:
                            results["skipped"].append(str(item))
                            continue

                        success = self.upload_package(
                            package_info["name"],
                            package_info["version"],
                            str(item),
                            consumer
                        )

                        if success:
                            results["uploaded"].append(str(item))
                        else:
                            results["failed"].append(str(item))

                        break

        return results

    def _upload_to_cloudsmith(self, package_name: str, version: str,
                            package_path: Optional[str], consumer: Optional[str]) -> bool:
        """Upload package to Cloudsmith."""
        if not self.api_key:
            print("ERROR: CLOUDSMITH_API_KEY not set")
            return False

        if not package_path:
            print(f"ERROR: Package path required for Cloudsmith upload: {package_name}")
            return False

        if self.dry_run:
            self.log(f"DRY RUN: Would upload {package_name} {version} to Cloudsmith")
            return True

        # Cloudsmith upload command
        cmd = [
            "cloudsmith", "push", "conan",
            "sparesparrow/sparetools",
            package_path,
            "--api-key", self.api_key
        ]

        if self.verbose:
            cmd.append("--verbose")

        try:
            result = subprocess.run(cmd, capture_output=not self.verbose, check=True, text=True)
            self.log(f"Successfully uploaded {package_name} {version} to Cloudsmith")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to upload to Cloudsmith: {e}")
            if not self.verbose:
                print(f"STDOUT: {e.stdout}")
                print(f"STDERR: {e.stderr}")
            return False

    def _upload_to_github(self, package_name: str, version: str,
                        package_path: Optional[str], consumer: Optional[str]) -> bool:
        """Upload package to GitHub Packages."""
        # GitHub Packages upload logic
        if self.dry_run:
            self.log(f"DRY RUN: Would upload {package_name} {version} to GitHub Packages")
            return True

        # Implementation would use GitHub CLI or REST API
        self.log("GitHub Packages upload not yet implemented")
        return False

    def _upload_to_local(self, package_name: str, version: str,
                        package_path: Optional[str], consumer: Optional[str]) -> bool:
        """Upload to local artifact repository."""
        local_repo = os.environ.get("SPARETOOLS_LOCAL_REPO", "./_Artifacts")

        if self.dry_run:
            self.log(f"DRY RUN: Would copy {package_name} {version} to {local_repo}")
            return True

        if not package_path:
            print(f"ERROR: Package path required for local upload: {package_name}")
            return False

        # Create destination directory
        dest_dir = Path(local_repo) / consumer / package_name / version
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy package
        import shutil
        dest_file = dest_dir / Path(package_path).name

        try:
            shutil.copy2(package_path, dest_file)
            self.log(f"Successfully copied {package_name} {version} to {dest_file}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to copy to local repo: {e}")
            return False

    def _parse_package_filename(self, filename: str) -> Optional[Dict[str, str]]:
        """Parse package information from filename.

        Args:
            filename: Package filename

        Returns:
            Dictionary with package info or None if unparseable
        """
        # Common patterns: package-version-hash.ext
        # Example: sparetools-openssl-3.3.2-abcdef123456.tar.gz

        try:
            # Remove extension
            name_without_ext = filename.rsplit('.', 1)[0]

            # Try to extract version
            parts = name_without_ext.split('-')
            if len(parts) < 2:
                return None

            # Last part before extension is likely version
            version = parts[-1]
            package_name = '-'.join(parts[:-1])

            return {
                "name": package_name,
                "version": version,
                "filename": filename
            }

        except Exception:
            return None

    def upload_sbom(self, package_name: str, sbom_path: str) -> bool:
        """Upload SBOM for a package.

        Args:
            package_name: Name of package
            sbom_path: Path to SBOM file

        Returns:
            True if upload successful
        """
        if not Path(sbom_path).exists():
            print(f"ERROR: SBOM file not found: {sbom_path}")
            return False

        if self.dry_run:
            self.log(f"DRY RUN: Would upload SBOM for {package_name}")
            return True

        # SBOM upload logic (could be to separate SBOM repository)
        self.log(f"SBOM upload not yet implemented for {package_name}")
        return False

    def generate_upload_report(self, results: Dict[str, Any],
                             output_file: str = "upload-report.json") -> str:
        """Generate upload report.

        Args:
            results: Upload results
            output_file: Output file path

        Returns:
            Path to report file
        """
        report = {
            "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "target": self.target,
            "results": results,
            "summary": {
                "total_attempted": results.get("total", 0),
                "successful": len(results.get("uploaded", [])),
                "failed": len(results.get("failed", [])),
                "skipped": len(results.get("skipped", []))
            }
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Upload report generated: {output_file}")
        return output_file


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Upload build artifacts for SpareTools"
    )

    parser.add_argument(
        "--target",
        choices=["cloudsmith", "github", "local"],
        default="cloudsmith",
        help="Upload target"
    )

    parser.add_argument(
        "--artifacts-dir",
        default="./build/artifacts",
        help="Directory containing artifacts"
    )

    parser.add_argument(
        "--consumer",
        help="Consumer domain for metadata"
    )

    parser.add_argument(
        "--package",
        help="Specific package to upload"
    )

    parser.add_argument(
        "--version",
        help="Package version"
    )

    parser.add_argument(
        "--api-key",
        help="API key for registry (or set CLOUDSMITH_API_KEY)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate upload without actually uploading"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--report",
        help="Generate upload report to file"
    )

    args = parser.parse_args()

    uploader = ArtifactUploader(
        target=args.target,
        api_key=args.api_key,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    results = None

    if args.package and args.version:
        # Upload specific package
        success = uploader.upload_package(
            args.package,
            args.version,
            consumer=args.consumer
        )
        results = {
            "total": 1,
            "uploaded": [args.package] if success else [],
            "failed": [args.package] if not success else [],
            "skipped": []
        }
    else:
        # Upload all artifacts from directory
        results = uploader.upload_artifacts(args.artifacts_dir, args.consumer)

    # Print summary
    print("Upload Summary:")
    print(f"  Total: {results.get('total', 0)}")
    print(f"  Uploaded: {len(results.get('uploaded', []))}")
    print(f"  Failed: {len(results.get('failed', []))}")
    print(f"  Skipped: {len(results.get('skipped', []))}")

    # Generate report if requested
    if args.report:
        uploader.generate_upload_report(results, args.report)

    success = len(results.get("failed", [])) == 0
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()