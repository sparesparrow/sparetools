from pathlib import Path
import shutil
import os
from typing import List

def deploy_openssl_profiles(force: bool = False, verbose: bool = True) -> None:
    conan_home = Path(os.environ.get("CONAN_USER_HOME", Path.home() / ".conan2"))
    profiles_dir = conan_home / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    package_root = Path(__file__).parent.parent
    source_profiles = package_root / "profiles"

    if not source_profiles.exists():
        if verbose:
            print(f"❌ No profiles found in {source_profiles}")
        return

    deployed_count = 0
    skipped_count = 0

    for profile_subdir in ["platforms", "compliance", "consumers"]:
        subdir = source_profiles / profile_subdir
        if not subdir.exists():
            continue
        for profile_file in subdir.glob("*.profile"):
            dest_profile = profiles_dir / profile_file.name
            if dest_profile.exists() and not force:
                if verbose:
                    print(f"ℹ️  Profile exists: {profile_file.name} (use --force)")
                skipped_count += 1
                continue
            shutil.copy2(profile_file, dest_profile)
            if verbose:
                print(f"📄 Deployed: {profile_file.name}")
            deployed_count += 1

    if verbose:
        print(f"\n✅ Deployed {deployed_count} profiles to {profiles_dir}")
        if skipped_count > 0:
            print(f"ℹ️  Skipped {skipped_count} existing profiles")


def list_openssl_profiles() -> List[str]:
    conan_home = Path(os.environ.get("CONAN_USER_HOME", Path.home() / ".conan2"))
    profiles_dir = conan_home / "profiles"
    if not profiles_dir.exists():
        return []
    profiles = []
    for profile_file in profiles_dir.glob("*.profile"):
        content = profile_file.read_text()
        if "openssl" in content.lower() or profile_file.stem.startswith(("linux-", "windows-", "fips-")):
            profiles.append(profile_file.stem)
    return sorted(profiles)
