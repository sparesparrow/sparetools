"""OpenSSL Perl Configure build method for SpareTools."""

import os
from conan.tools.gnu import Autotools


def build_openssl(conanfile):
    """Build OpenSSL using Perl Configure method.

    Args:
        conanfile: The ConanFile instance
    """
    # Determine target based on platform
    target = _get_openssl_target(conanfile)

    configure_args = [
        f"--prefix={conanfile.package_folder}",
        f"--openssldir={os.path.join(conanfile.package_folder, 'ssl')}",
        "no-tests",  # Skip tests for faster builds
        "no-docs",   # Skip documentation
    ]

    if conanfile.options.shared:
        configure_args.append("shared")
    else:
        configure_args.append("no-shared")

    if conanfile.options.fips:
        configure_args.append("enable-fips")

    if conanfile.options.no_threads:
        configure_args.append("no-threads")

    if conanfile.options.no_stdlib_check:
        configure_args.append("-Wno-stdlib-check")

    # Platform-specific arguments
    if conanfile.settings.os == "Macos":
        # macOS deployment target
        deployment_target = os.environ.get("MACOSX_DEPLOYMENT_TARGET", "13.0")
        configure_args.append(f"-mmacosx-version-min={deployment_target}")

    elif conanfile.settings.os == "Windows":
        # Windows-specific settings
        if conanfile.settings.compiler == "msvc":
            configure_args.append("-FS")  # Force synchronous PDB writes

    conanfile.output.info(f"OpenSSL target: {target}")
    conanfile.output.info(f"Configure args: {' '.join(configure_args)}")

    # Run Perl Configure
    conanfile.run(f"perl Configure {target} {' '.join(configure_args)}")

    # Build
    autotools = Autotools(conanfile)
    autotools.make()

    # Install
    autotools.install()


def _get_openssl_target(conanfile):
    """Get OpenSSL target string based on Conan settings.

    Args:
        conanfile: The ConanFile instance

    Returns:
        str: OpenSSL target string
    """
    os_name = str(conanfile.settings.os)
    arch = str(conanfile.settings.arch)
    compiler = str(conanfile.settings.compiler)

    if os_name == "Linux":
        if arch == "x86_64":
            return "linux-x86_64"
        elif arch == "armv8":
            return "linux-aarch64"
        elif arch == "armv7":
            return "linux-armv4"
        elif arch == "x86":
            return "linux-elf"

    elif os_name == "Macos":
        if arch == "x86_64":
            return "darwin64-x86_64"
        elif arch == "arm64":
            return "darwin64-arm64"

    elif os_name == "Windows":
        if compiler == "msvc":
            if arch == "x86_64":
                return "VC-WIN64A"
            else:
                return "VC-WIN32"
        elif compiler == "gcc":
            if arch == "x86_64":
                return "mingw64"
            else:
                return "mingw"

    elif os_name == "Android":
        if arch == "armv8":
            return "android-arm64"
        elif arch == "armv7":
            return "android-arm"
        elif arch == "x86_64":
            return "android-x86_64"
        elif arch == "x86":
            return "android-x86"

    elif os_name == "iOS":
        if arch == "arm64":
            return "ios64-xcrun"
        elif arch == "x86_64":
            return "iossimulator-xcrun"

    # Default fallback
    return "linux-x86_64"