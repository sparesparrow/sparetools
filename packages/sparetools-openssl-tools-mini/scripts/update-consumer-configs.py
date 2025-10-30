#!/usr/bin/env python3
"""
Update consumer configurations to use new user/channel references
"""

import argparse
import os
import re
from pathlib import Path
import json


def update_conanfile_txt(file_path, user="sparesparrow", channel="stable"):
    """Update conanfile.txt with proper user/channel references"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Backup original
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w') as f:
            f.write(content)

        # Update package references
        # Look for OpenSSL ecosystem packages and add user/channel if missing
        lines = content.split('\n')
        updated_lines = []

        for line in lines:
            original_line = line.strip()

            # Skip comments and empty lines
            if not original_line or original_line.startswith('#'):
                updated_lines.append(line)
                continue

            # Check for package references
            # Match: package/version or package/version@user/channel
            match = re.match(r'^(\w+)/([\d\.]+(?:-[\w\.-]+)?)(?:@(\w+)/(\w+))?', original_line)
            if match:
                package, version, existing_user, existing_channel = match.groups()

                # If it's an OpenSSL ecosystem package and doesn't have user/channel
                if package.startswith(('openssl', 'fips')) and not existing_user:
                    # Add user/channel
                    line = f"{package}/{version}@{user}/{channel}"
                    print(f"  Updated: {original_line} -> {line}")
                elif existing_user and existing_channel:
                    # Update existing reference if needed
                    if existing_user != user or existing_channel != channel:
                        new_ref = f"{package}/{version}@{user}/{channel}"
                        print(f"  Updated: {original_line} -> {new_ref}")
                        line = new_ref

            updated_lines.append(line)

        # Write updated content
        new_content = '\n'.join(updated_lines)
        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"Updated: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            # Remove backup if no changes
            os.remove(backup_path)
            return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def create_consumer_examples(base_dir="consumer-examples", user="sparesparrow"):
    """Create example consumer configurations"""
    examples_dir = Path(base_dir)
    examples_dir.mkdir(exist_ok=True)

    # Stable channel example
    stable_conanfile = f"""[requires]
openssl/3.4.1@{user}/stable
openssl-build-tools/1.2.0@{user}/stable

[generators]
cmake
"""
    with open(examples_dir / "conanfile-stable.txt", 'w') as f:
        f.write(stable_conanfile)

    # Development channel example
    dev_conanfile = f"""[requires]
openssl/3.4.1@{user}/dev
openssl-build-tools/1.2.0@{user}/dev

[generators]
cmake
"""
    with open(examples_dir / "conanfile-dev.txt", 'w') as f:
        f.write(dev_conanfile)

    # Testing channel example
    testing_conanfile = f"""[requires]
openssl/3.4.1@{user}/testing
openssl-build-tools/1.2.0@{user}/testing

[generators]
cmake
"""
    with open(examples_dir / "conanfile-testing.txt", 'w') as f:
        f.write(testing_conanfile)

    # Environment-specific example
    env_conanfile = f"""[requires]
# Use environment variables for user/channel
openssl/3.4.1@${{CONAN_USER}}/${{CONAN_CHANNEL}}
openssl-build-tools/1.2.0@${{CONAN_USER}}/${{CONAN_CHANNEL}}

[generators]
cmake
"""
    with open(examples_dir / "conanfile-env.txt", 'w') as f:
        f.write(env_conanfile)

    print(f"Created consumer examples in {examples_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Update consumer configurations for user/channel references")
    parser.add_argument("--user", default="sparesparrow", help="Conan user")
    parser.add_argument("--channel", default="stable", help="Conan channel")
    parser.add_argument("--search-path", default=".", help="Path to search for conanfile.txt files")
    parser.add_argument("--create-examples", action="store_true", help="Create example consumer configurations")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")

    args = parser.parse_args()

    print("Conan Consumer Configuration Update")
    print("=" * 40)
    print(f"Target reference: {args.user}/{args.channel}")
    print()

    if args.create_examples:
        create_consumer_examples(user=args.user)
        return

    # Find conanfile.txt files
    search_path = Path(args.search_path)
    conanfiles = list(search_path.rglob("conanfile.txt"))

    print(f"Found {len(conanfiles)} conanfile.txt files")

    updated_count = 0
    for conanfile in conanfiles:
        print(f"Processing: {conanfile}")
        if not args.dry_run:
            if update_conanfile_txt(str(conanfile), args.user, args.channel):
                updated_count += 1
        else:
            # For dry run, just count files that would be updated
            try:
                with open(conanfile, 'r') as f:
                    content = f.read()
                if re.search(r'(\w+)/([\d\.]+)(@\w+/\w+)?', content):
                    print(f"Would update: {conanfile}")
                    updated_count += 1
            except Exception as e:
                print(f"Error reading {conanfile}: {e}")

    print(f"\nProcessed {updated_count} files")

    if not args.dry_run:
        print("\nNext steps:")
        print("1. Test consumer configurations: conan install .")
        print("2. Update any hardcoded references in your code")
        print("3. Verify builds work with new references")


if __name__ == "__main__":
    main()