#!/usr/bin/env python3
"""
Migrate Conan package references to use user/channel format
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
import json


def run_conan_command(cmd, check=True):
    """Run a Conan command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return None
        return result
    except Exception as e:
        print(f"Error running command: {e}")
        return None


def get_local_packages():
    """Get list of local Conan packages"""
    result = run_conan_command("conan list '*' --format=json")
    if not result:
        return []

    try:
        data = json.loads(result.stdout)
        packages = []

        # Handle different Conan versions
        if "Local Cache" in data:
            cache_data = data["Local Cache"]
        else:
            cache_data = data

        for package_ref, package_info in cache_data.items():
            packages.append(package_ref)

        return packages
    except Exception as e:
        print(f"Error parsing package list: {e}")
        return []


def migrate_conanfile_txt(file_path, old_user=None, old_channel=None, new_user=None, new_channel=None):
    """Migrate references in a conanfile.txt"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content

        # Pattern to match package references like package/version@user/channel
        # Also match references without user/channel
        patterns = [
            r'(\w+)/([\d\.]+)(@\w+/\w+)?',  # package/version@user/channel or package/version
        ]

        for pattern in patterns:
            def replace_ref(match):
                package = match.group(1)
                version = match.group(2)
                existing_ref = match.group(3) if len(match.groups()) > 2 else None

                # If already has user/channel, check if it needs updating
                if existing_ref:
                    current_user, current_channel = existing_ref[1:].split('/')  # Remove @
                    if (old_user and current_user == old_user) or (old_channel and current_channel == old_channel):
                        return f"{package}/{version}@{new_user or current_user}/{new_channel or current_channel}"
                    return match.group(0)  # Keep as is
                else:
                    # Add user/channel to reference without it
                    if package.startswith(('openssl', 'fips')):  # OpenSSL ecosystem packages
                        return f"{package}/{version}@{new_user}/{new_channel}"
                    return match.group(0)  # Keep other packages as is

            content = re.sub(pattern, replace_ref, content)

        if content != original_content:
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w') as f:
                f.write(original_content)
            print(f"Created backup: {backup_path}")

            # Write updated content
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Updated: {file_path}")

            return True
        else:
            print(f"No changes needed: {file_path}")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def migrate_remote_references(remote_name, old_user=None, old_channel=None, new_user=None, new_channel=None):
    """Migrate package references in remote"""
    print(f"Migrating remote: {remote_name}")

    # This would require more complex logic to update remote packages
    # For now, we'll focus on local migration and documentation
    print("Remote migration requires manual intervention:")
    print("1. Update CI/CD pipelines to use new user/channel")
    print("2. Re-publish packages with new references")
    print("3. Update downstream consumers")


def main():
    parser = argparse.ArgumentParser(description="Migrate Conan package references to user/channel format")
    parser.add_argument("--old-user", help="Old user to replace")
    parser.add_argument("--old-channel", help="Old channel to replace")
    parser.add_argument("--new-user", default="sparesparrow", help="New user (default: sparesparrow)")
    parser.add_argument("--new-channel", default="stable", help="New channel (default: stable)")
    parser.add_argument("--conanfile", help="Specific conanfile.txt to migrate")
    parser.add_argument("--search-path", default=".", help="Path to search for conanfile.txt files")
    parser.add_argument("--migrate-local", action="store_true", help="Migrate local Conan cache")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")

    args = parser.parse_args()

    print("Conan Reference Migration Tool")
    print("=" * 40)
    print(f"Migrating to: {args.new_user}/{args.new_channel}")
    if args.old_user or args.old_channel:
        print(f"Replacing: {args.old_user or '*'}@{args.old_channel or '*'}")
    print()

    # Find conanfile.txt files
    conanfiles = []
    if args.conanfile:
        conanfiles = [Path(args.conanfile)]
    else:
        search_path = Path(args.search_path)
        conanfiles = list(search_path.rglob("conanfile.txt"))

    print(f"Found {len(conanfiles)} conanfile.txt files")

    # Migrate conanfile.txt files
    migrated_count = 0
    for conanfile in conanfiles:
        print(f"Processing: {conanfile}")
        if not args.dry_run:
            if migrate_conanfile_txt(str(conanfile), args.old_user, args.old_channel, args.new_user, args.new_channel):
                migrated_count += 1
        else:
            # For dry run, just check if changes would be made
            try:
                with open(conanfile, 'r') as f:
                    content = f.read()
                if re.search(r'(\w+)/([\d\.]+)(@\w+/\w+)?', content):
                    print(f"Would migrate: {conanfile}")
                    migrated_count += 1
            except Exception as e:
                print(f"Error reading {conanfile}: {e}")

    print(f"\nMigration complete: {migrated_count} files processed")

    # Local cache migration (basic)
    if args.migrate_local:
        print("\nMigrating local Conan cache...")
        packages = get_local_packages()
        openssl_packages = [p for p in packages if p.startswith(('openssl', 'fips'))]

        if openssl_packages:
            print(f"Found {len(openssl_packages)} OpenSSL-related packages in local cache")
            print("Local cache migration requires:")
            print("1. Remove old packages: conan remove <package> -f")
            print("2. Re-install with new references: conan install <new-ref>")
        else:
            print("No OpenSSL packages found in local cache")

    # Summary and next steps
    print("\nNext Steps:")
    print("1. Test the migrated conanfile.txt files")
    print("2. Update any hardcoded references in scripts/code")
    print("3. Re-publish packages with new user/channel references")
    print("4. Update downstream consumers")


if __name__ == "__main__":
    main()