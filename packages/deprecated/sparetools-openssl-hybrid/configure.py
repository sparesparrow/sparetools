#!/usr/bin/env python3
"""
OpenSSL Configure Script - Python replacement for Configure

Configures OpenSSL build system with Python-based approach.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class OpenSSLConfigurer:
    """OpenSSL build configuration handler."""

    def __init__(self):
        self.debug = False
        self.quiet = False
        self.target: Optional[str] = None
        self.prefix: Optional[str] = None
        self.openssldir: Optional[str] = None
        self.options: Set[str] = set()
        self.disabled_features: Set[str] = set()
        self.enabled_features: Set[str] = set()
        self.defines: Dict[str, str] = {}
        self.includes: List[str] = []
        self.libdirs: List[str] = []
        self.libs: List[str] = []

        # Platform detection
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.is_64bit = sys.maxsize > 2**32

        # Build configuration
        self.build_config = {
            'shared': False,
            'threads': True,
            'asm': True,
            'fips': False,
            'zlib': True,
            'no_shared': False,
            'no_threads': False,
            'no_asm': False,
            'enable_fips': False,
        }

    def detect_platform(self) -> str:
        """Detect the build platform and return appropriate target."""
        system = self.system
        machine = self.machine

        # Platform mapping
        platform_map = {
            ('linux', 'x86_64'): 'linux-x86_64',
            ('linux', 'i386'): 'linux-x86',
            ('linux', 'i686'): 'linux-x86',
            ('linux', 'aarch64'): 'linux-aarch64',
            ('linux', 'armv7l'): 'linux-armv4',
            ('darwin', 'x86_64'): 'darwin64-x86_64-cc',
            ('darwin', 'arm64'): 'darwin64-arm64-cc',
            ('freebsd', 'x86_64'): 'BSD-x86_64',
            ('openbsd', 'x86_64'): 'BSD-x86_64',
            ('netbsd', 'x86_64'): 'BSD-x86_64',
            ('windows', 'x86_64'): 'VC-WIN64A',
            ('windows', 'i386'): 'VC-WIN32',
            ('windows', 'amd64'): 'VC-WIN64A',
        }

        return platform_map.get((system, machine), 'linux-x86_64')

    def parse_arguments(self, args: List[str]) -> None:
        """Parse command line arguments."""
        i = 0
        while i < len(args):
            arg = args[i]

            if arg.startswith('no-'):
                # Disabled feature
                feature = arg[3:]  # Remove 'no-' prefix
                self.disabled_features.add(feature)
                if feature in self.build_config:
                    self.build_config[feature] = False
            elif arg.startswith('enable-'):
                # Enabled feature
                feature = arg[7:]  # Remove 'enable-' prefix
                self.enabled_features.add(feature)
                if f"enable_{feature}" in self.build_config:
                    self.build_config[f"enable_{feature}"] = True
                elif feature in self.build_config:
                    self.build_config[feature] = True
            elif arg.startswith('-D'):
                # Define
                define = arg[2:]
                if '=' in define:
                    key, value = define.split('=', 1)
                    self.defines[key] = value
                else:
                    self.defines[define] = ''
            elif arg.startswith('-I'):
                # Include directory
                self.includes.append(arg[2:])
            elif arg.startswith('-L'):
                # Library directory
                self.libdirs.append(arg[2:])
            elif arg.startswith('-l'):
                # Library
                self.libs.append(arg[2:])
            elif arg == '--help' or arg == '-h':
                self.show_help()
                sys.exit(0)
            elif arg == '--debug':
                self.debug = True
            elif arg == '--quiet':
                self.quiet = True
            elif arg.startswith('--prefix='):
                self.prefix = arg.split('=', 1)[1]
            elif arg == '--prefix':
                # Prefix value will be in next argument
                if i + 1 < len(args):
                    self.prefix = args[i + 1]
                    i += 1
            elif arg.startswith('--openssldir='):
                self.openssldir = arg.split('=', 1)[1]
            elif arg == '--openssldir':
                # Openssldir value will be in next argument
                if i + 1 < len(args):
                    self.openssldir = args[i + 1]
                    i += 1
            elif not arg.startswith('-'):
                # Target/platform specification
                if not self.target:
                    self.target = arg
                else:
                    print(f"Warning: Multiple targets specified, using {self.target}", file=sys.stderr)
            else:
                print(f"Warning: Unknown option {arg}", file=sys.stderr)

            i += 1

    def show_help(self) -> None:
        """Display help information."""
        help_text = """
OpenSSL Configure Script

Usage: python configure.py [options] [target]

Options:
    no-<feature>        Disable feature
    enable-<feature>    Enable feature
    -D<define>          Add preprocessor define
    -I<dir>            Add include directory
    -L<dir>            Add library directory
    -l<lib>            Add library
    --debug            Enable debug output
    --quiet            Suppress non-essential output
    --help             Show this help

Common features:
    no-shared          Build static libraries only
    no-threads         Disable threading support
    no-asm            Disable assembly optimizations
    enable-fips        Enable FIPS mode

Common targets:
    linux-x86_64       Linux x86_64
    darwin64-x86_64-cc macOS x86_64
    VC-WIN64A         Windows x86_64
"""
        print(help_text)

    def validate_configuration(self) -> bool:
        """Validate the build configuration."""
        errors = []

        # Check for conflicting options
        if self.build_config['no_shared'] and self.build_config['shared']:
            errors.append("Cannot specify both 'no-shared' and 'shared'")

        if self.build_config['no_threads'] and self.build_config['threads']:
            errors.append("Cannot specify both 'no-threads' and 'threads'")

        if self.build_config['no_asm'] and self.build_config['asm']:
            errors.append("Cannot specify both 'no-asm' and 'asm'")

        if errors:
            for error in errors:
                print(f"Error: {error}", file=sys.stderr)
            return False

        return True

    def generate_config_files(self) -> None:
        """Generate configuration files."""
        self.generate_configdata_pm()
        self.generate_buildinfo_h()
        self.generate_makefile()

    def generate_configdata_pm(self) -> None:
        """Generate configdata.pm file."""
        if not self.quiet:
            print("Generating configdata.pm...")

        with open('configdata.pm', 'w') as f:
            f.write("# Generated by configure.py\n")
            f.write("# Do not edit manually\n\n")

            f.write("package configdata;\n\n")

            # Write configuration data
            f.write("our %config = (\n")
            for key, value in self.build_config.items():
                f.write(f"    '{key}' => {value},\n")

            # Add directory configurations
            prefix = self.prefix or '/usr/local/ssl'
            openssldir = self.openssldir or os.path.join(prefix, 'ssl')

            f.write(f"    'prefix' => '{prefix}',\n")
            f.write(f"    'openssldir' => '{openssldir}',\n")
            f.write(f"    'libdir' => '{os.path.join(prefix, 'lib')}',\n")
            f.write(f"    'includedir' => '{os.path.join(prefix, 'include')}',\n")
            f.write(f"    'enginesdir' => '{os.path.join(openssldir, 'engines')}',\n")
            f.write(f"    'modulesdir' => '{os.path.join(openssldir, 'modules')}',\n")

            f.write(");\n\n")

            # Write target information
            f.write(f"our $target = '{self.target or 'unknown'}';\n\n")

            # Write defines
            f.write("our %defines = (\n")
            for key, value in self.defines.items():
                f.write(f"    '{key}' => '{value}',\n")

            # Add directory defines
            f.write(f"    'OPENSSLDIR' => '{openssldir}',\n")
            f.write(f"    'ENGINESDIR' => '{os.path.join(openssldir, 'engines')}',\n")
            f.write(f"    'MODULESDIR' => '{os.path.join(openssldir, 'modules')}',\n")

            f.write(");\n\n")

            f.write("1;\n")

    def generate_buildinfo_h(self) -> None:
        """Generate buildinf.h header file using Python mkbuildinf.py."""
        if not self.quiet:
            print("Generating buildinf.h...")

        try:
            # Use the Python mkbuildinf.py script
            import subprocess
            import platform

            # Get platform information for the mkbuildinf script
            platform_info = platform.platform()
            cflags = self._get_cflags()

            # Run mkbuildinf.py like the original Perl script: cflags platform
            cmd = [sys.executable, 'util/python/mkbuildinf.py', cflags, platform_info]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())

            if result.returncode == 0:
                if not self.quiet:
                    print("? buildinf.h generated successfully")
                # Copy buildinf.h to the correct location
                if os.path.exists('buildinf.h'):
                    os.makedirs('include/openssl', exist_ok=True)
                    import shutil
                    shutil.copy('buildinf.h', 'include/openssl/buildinf.h')
            else:
                print(f"Warning: mkbuildinf.py failed: {result.stderr}")
                # Fallback generation
                self._generate_fallback_buildinf()

        except Exception as e:
            print(f"Warning: Error generating buildinf.h: {e}")
            self._generate_fallback_buildinf()

    def _generate_fallback_buildinf(self) -> None:
        """Generate fallback buildinf.h if mkbuildinf.py fails."""
        platform_info = platform.platform()
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')

        with open('buildinf.h', 'w') as f:
            f.write("/*\n")
            f.write(" * WARNING: do not edit!\n")
            f.write(" * Generated by configure.py (fallback)\n")
            f.write(" */\n\n")

            f.write("#ifndef OPENSSL_BUILDINFO_H\n")
            f.write("#define OPENSSL_BUILDINFO_H\n\n")

            f.write(f'#define PLATFORM "platform: {platform_info}"\n')
            f.write(f'#define DATE "built on: {date_str}"\n')

            f.write('\n/*\n')
            f.write(' * Fallback compiler_flags\n')
            f.write(' */\n')
            f.write('static const char compiler_flags[] = {\n')
            f.write("    'c', 'o', 'm', 'p', 'i', 'l', 'e', 'r', ':', ' ', 'u', 'n', 'k', 'n', 'o', 'w', 'n', '\\0'\n")
            f.write('};\n')

            f.write("\n#endif /* OPENSSL_BUILDINFO_H */\n")

    def generate_makefile(self) -> bool:
        """Generate Makefile directly without calling Perl Configure script."""
        if not self.quiet:
            print("?? Generating Makefile with Python configure...")

        try:
            # Set defaults
            prefix = self.prefix or '/usr/local/ssl'
            openssldir = self.openssldir or os.path.join(prefix, 'ssl')

            # Store configuration for use by Makefile
            self._install_prefix = prefix
            self._openssldir = openssldir

            # Generate Makefile directly
            makefile_content = self._generate_makefile_content(prefix, openssldir)

            with open('Makefile', 'w') as f:
                f.write(makefile_content)

            if not self.quiet:
                print("? Makefile generated successfully")

            # Generate configdata.pm
            self.generate_configdata_pm()

            # Generate build information
            self.generate_buildinfo_h()

            # Generate CPS file for modern build system integration
            self.generate_cps_file()

            return True

        except Exception as e:
            print(f"? Makefile generation failed: {e}")
            return False

    def _generate_makefile_content(self, prefix: str, openssldir: str) -> str:
        """Generate complete Makefile content."""
        # Detect compiler and flags
        cc = self._detect_compiler()
        cflags = self._get_cflags()
        ldflags = self._get_ldflags()
        libs = self._get_libs()

        # Build configuration based on options
        shared_flag = "SHARED" if self.build_config.get('shared', False) else "NO_SHARED"
        threads_flag = "THREADS" if self.build_config.get('threads', True) else "NO_THREADS"
        asm_flag = "ASM" if self.build_config.get('asm', True) else "NO_ASM"
        fips_flag = "FIPS" if self.build_config.get('fips', False) else "NO_FIPS"

        # Platform-specific settings
        platform_settings = self._get_platform_settings()

        makefile = f'''# Generated by Python configure.py - Modern OpenSSL build system
# Do not edit manually - regenerate with: python3 configure.py [options]

# Installation paths
PREFIX = {prefix}
OPENSSLDIR = {openssldir}
INSTALLTOP = $(PREFIX)
LIBDIR = $(INSTALLTOP)/lib
INCDIR = $(INSTALLTOP)/include
BINDIR = $(INSTALLTOP)/bin
MANDIR = $(INSTALLTOP)/share/man

# Compiler and tools
CC = {cc}
CXX = g++
AR = ar
RANLIB = ranlib
MAKE = make

# Compiler flags
CFLAGS = {cflags}
CXXFLAGS = $(CFLAGS)
LDFLAGS = {ldflags}
LIBS = {libs}

# Directory defines for C preprocessor
CPPFLAGS = -DOPENSSLDIR=\\\"{openssldir}\\\" -DENGINESDIR=\\\"{os.path.join(openssldir, 'engines')}\\\" -DMODULESDIR=\\\"{os.path.join(openssldir, 'modules')}\\\"

# Platform-specific settings
{platform_settings}

# Build configuration flags
BUILD_CONFIG = {shared_flag} {threads_flag} {asm_flag} {fips_flag}

# Main targets
all: build_libs build_apps

build_libs: providers libcrypto.a libssl.a

build_apps: build_libs apps/openssl

# Library targets - build directly without subdirectories
libcrypto.a: crypto_objects
	@echo "Building libcrypto.a..."
	$(AR) rcs libcrypto.a $(CRYPTO_OBJECTS)
	$(RANLIB) libcrypto.a

libssl.a: libcrypto.a ssl_objects
	@echo "Building libssl.a..."
	$(AR) rcs libssl.a $(SSL_OBJECTS)
	$(RANLIB) libssl.a

# Application targets
apps/openssl: apps/openssl.o
	@echo "Building openssl binary..."
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) apps/openssl.o $(LIBS) -o apps/openssl

# Object compilation rules
%.o: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -Iinclude -I. -Iproviders/common/include -Iproviders/implementations/include -c $< -o $@

# Source file collections - exclude architecture-specific files when not supported
CRYPTO_SOURCES = $(wildcard crypto/*.c crypto/*/*.c crypto/*/*/*.c)
CRYPTO_SOURCES := $(filter-out crypto/arm%,$(CRYPTO_SOURCES))
CRYPTO_SOURCES := $(filter-out crypto/ia64%,$(CRYPTO_SOURCES))
CRYPTO_OBJECTS = $(CRYPTO_SOURCES:.c=.o)

SSL_SOURCES = $(wildcard ssl/*.c ssl/*/*.c)
SSL_SOURCES := $(filter-out ssl/arm%,$(SSL_SOURCES))
SSL_OBJECTS = $(SSL_SOURCES:.c=.o)

PROVIDERS_SOURCES = $(wildcard providers/*.c providers/*/*.c providers/*/*/*.c)
PROVIDERS_SOURCES := $(filter-out providers/fips%,$(PROVIDERS_SOURCES))  # Exclude FIPS for now
PROVIDERS_SOURCES := $(filter-out providers/common/der/%,$(PROVIDERS_SOURCES))  # Exclude DER files that depend on FIPS
PROVIDERS_SOURCES := $(filter-out providers/common/securitycheck_fips.c,$(PROVIDERS_SOURCES))  # Exclude FIPS security checks
PROVIDERS_SOURCES := $(filter-out providers/implementations/asymciphers/rsa_enc.c,$(PROVIDERS_SOURCES))  # Exclude RSA encryption with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_desx.c,$(PROVIDERS_SOURCES))  # Exclude DESX with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_desx_hw.c,$(PROVIDERS_SOURCES))  # Exclude DESX HW with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_rc5.c,$(PROVIDERS_SOURCES))  # Exclude RC5 cipher (patented algorithm)
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_rc5_hw.c,$(PROVIDERS_SOURCES))  # Exclude RC5 HW cipher
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_tdes.c,$(PROVIDERS_SOURCES))  # Exclude TDES with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_tdes_common.c,$(PROVIDERS_SOURCES))  # Exclude TDES common with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_tdes_default.c,$(PROVIDERS_SOURCES))  # Exclude TDES default with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_tdes_default_hw.c,$(PROVIDERS_SOURCES))  # Exclude TDES default HW with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_tdes_hw.c,$(PROVIDERS_SOURCES))  # Exclude TDES HW with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_tdes_wrap.c,$(PROVIDERS_SOURCES))  # Exclude TDES wrap with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/ciphers/cipher_tdes_wrap_hw.c,$(PROVIDERS_SOURCES))  # Exclude TDES wrap HW with FIPS indicators
PROVIDERS_SOURCES := $(filter-out providers/implementations/digests/md2_prov.c,$(PROVIDERS_SOURCES))  # Exclude MD2 provider (deprecated)
PROVIDERS_SOURCES := $(filter-out providers/implementations/digests/md4_prov.c,$(PROVIDERS_SOURCES))  # Exclude MD4 provider (deprecated)
PROVIDERS_OBJECTS = $(PROVIDERS_SOURCES:.c=.o)

# Pseudo targets for object compilation
crypto_objects: $(CRYPTO_OBJECTS)
ssl_objects: $(SSL_OBJECTS)
providers: $(PROVIDERS_OBJECTS)

# Installation targets
install: install_libs install_headers install_apps install_docs

install_libs: build_libs
	@echo "Installing libraries to $(LIBDIR)..."
	@mkdir -p $(LIBDIR)
	@cp libcrypto.a $(LIBDIR)/
	@cp libssl.a $(LIBDIR)/
	@if [ "$(BUILD_CONFIG)" = "*SHARED*" ]; then \\
		cp libcrypto.so $(LIBDIR)/ 2>/dev/null || true; \\
		cp libssl.so $(LIBDIR)/ 2>/dev/null || true; \\
	fi

install_headers:
	@echo "Installing headers to $(INCDIR)..."
	@mkdir -p $(INCDIR)/openssl
	@cp -r include/openssl/* $(INCDIR)/openssl/

install_apps: build_apps
	@echo "Installing applications to $(BINDIR)..."
	@mkdir -p $(BINDIR)
	@cp apps/openssl $(BINDIR)/

install_docs:
	@echo "Installing documentation to $(MANDIR)..."
	@mkdir -p $(MANDIR)/man1 $(MANDIR)/man3
	@cp doc/man/* $(MANDIR)/man1/ 2>/dev/null || true
	@cp doc/man/* $(MANDIR)/man3/ 2>/dev/null || true

# Install only libraries (for Conan packaging)
install_sw: install_libs install_headers

# Install SSL directories
install_ssldirs:
	@echo "Creating SSL directories..."
	@mkdir -p $(OPENSSLDIR)/certs
	@mkdir -p $(OPENSSLDIR)/private
	@mkdir -p $(OPENSSLDIR)/misc

# Development targets
install_dev: install_sw install_ssldirs
	@echo "Development installation completed"

# Clean targets
clean:
	@echo "Cleaning build artifacts..."
	@rm -f *.o crypto/*.o crypto/*/*.o ssl/*.o apps/*.o providers/*.o providers/*/*.o
	@rm -f libcrypto.a libssl.a
	@rm -f apps/openssl
	@find . -name "*.so" -delete

distclean: clean
	@echo "Removing generated files..."
	@rm -f Makefile configdata.pm include/openssl/buildinf.h openssl.cps
	@rm -rf $(LIBDIR) $(INCDIR) $(BINDIR)

# Test target
test: all
	@echo "Running tests..."
	@cd test && $(MAKE) test

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Build everything"
	@echo "  build_libs   - Build libraries only"
	@echo "  build_apps   - Build applications"
	@echo "  install      - Install everything"
	@echo "  install_sw   - Install software only (for packaging)"
	@echo "  install_dev  - Install for development"
	@echo "  clean        - Clean build artifacts"
	@echo "  distclean    - Clean everything"
	@echo "  test         - Run tests"
	@echo "  help         - Show this help"

.PHONY: all build_libs build_apps install install_sw install_ssldirs install_dev clean distclean test help crypto_objects ssl_objects providers
'''

        return makefile

    def _detect_compiler(self) -> str:
        """Detect available compiler."""
        # Try to detect compiler from environment or system
        cc = os.environ.get('CC', 'gcc')
        if os.path.exists(cc) or shutil.which(cc):
            return cc

        # Fallback to common compilers
        for compiler in ['gcc', 'clang', 'cc']:
            if shutil.which(compiler):
                return compiler

        return 'gcc'  # Ultimate fallback

    def _get_cflags(self) -> str:
        """Get appropriate C compiler flags."""
        base_flags = "-O3 -Wall -Wextra"

        if self.build_config.get('asm', True):
            base_flags += " -DASM"

        if self.build_config.get('threads', True):
            base_flags += " -DTHREADS"

        if self.build_config.get('fips', False):
            base_flags += " -DFIPS -DFIPS_MODULE"

        # Platform specific flags
        if self.system == 'linux':
            base_flags += " -DLINUX"

        # Architecture specific flags
        if self.machine in ['x86_64', 'amd64']:
            base_flags += " -DX86_64"
        elif self.machine in ['i386', 'i686']:
            base_flags += " -DX86"
        elif self.machine.startswith('arm') or self.machine == 'aarch64':
            base_flags += " -DARM"

        # Position independent code for shared libraries
        if self.build_config.get('shared', False):
            base_flags += " -fPIC"

        return base_flags

    def _get_ldflags(self) -> str:
        """Get appropriate linker flags."""
        flags = ""

        if self.system == 'linux':
            flags += "-ldl -lpthread"

        if self.build_config.get('shared', False):
            flags += " -shared"

        return flags

    def _get_libs(self) -> str:
        """Get required libraries."""
        if self.system == 'linux':
            return "-lcrypto -lssl -ldl -lpthread"
        return ""

    def _get_platform_settings(self) -> str:
        """Get platform-specific Makefile settings."""
        settings = []

        if self.system == 'linux':
            settings.append("# Linux-specific settings")
            settings.append("PLATFORM = linux")
            settings.append("KERNEL = linux")

        elif self.system == 'darwin':
            settings.append("# macOS-specific settings")
            settings.append("PLATFORM = darwin")
            settings.append("KERNEL = darwin")

        elif self.system == 'windows':
            settings.append("# Windows-specific settings")
            settings.append("PLATFORM = windows")
            settings.append("KERNEL = windows")

        return "\n".join(settings)

    def show_configuration_summary(self) -> None:
        """Display configuration summary."""
        print("\n" + "="*50)
        print("OpenSSL Configuration Summary")
        print("="*50)
        print(f"Target: {self.target}")
        print(f"Platform: {self.system} {self.machine}")
        print(f"64-bit: {self.is_64bit}")

        print("\nBuild Options:")
        for key, value in sorted(self.build_config.items()):
            print(f"  {key}: {value}")

        if self.defines:
            print("\nDefines:")
            for key, value in sorted(self.defines.items()):
                print(f"  {key}={value}")

        if self.includes:
            print("\nInclude directories:")
            for inc in self.includes:
                print(f"  {inc}")

        if self.libdirs:
            print("\nLibrary directories:")
            for libdir in self.libdirs:
                print(f"  {libdir}")

        if self.libs:
            print("\nLibraries:")
            for lib in self.libs:
                print(f"  {lib}")

        print("\nConfiguration completed successfully!")
        print("Run 'make' to build OpenSSL.")

    def run(self, args: List[str]) -> int:
        """Main execution method."""
        # Detect platform if no target specified
        if not self.target:
            self.target = self.detect_platform()

        # Parse command line arguments
        self.parse_arguments(args)

        if self.debug:
            print(f"Debug: Target = {self.target}")
            print(f"Debug: System = {self.system}")
            print(f"Debug: Machine = {self.machine}")

        # Validate configuration
        if not self.validate_configuration():
            return 1

        # Generate configuration files
        self.generate_config_files()

        # Generate Makefile by calling traditional Configure
        if not self.generate_makefile():
            return 1

        # This script only handles configuration, not building
        # The actual build will be handled by the calling conanfile.py

        # Show summary
        if not self.quiet:
            self.show_configuration_summary()

        return 0

    def generate_cps_file(self) -> None:
        """Generate CPS file for modern build system integration (CppCon 2024 approach)"""
        # Try to read version from VERSION.dat
        version = "4.0.4-dev"
        version_file = os.path.join(os.getcwd(), "VERSION.dat")
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    for line in f:
                        if line.startswith("VERSION="):
                            version = line.split("=")[1].strip().strip('"')
                            break
            except Exception:
                pass

        # Determine library extension based on shared option
        lib_ext = ".so" if self.build_config.get('shared', False) else ".a"

        cps_data = {
            "cps_version": "0.13.0",
            "name": "openssl",
            "version": version,
            "components": {
                "crypto": {
                    "type": "library",
                    "location": f"@prefix@/lib/libcrypto{lib_ext}",
                    "includes": ["@prefix@/include"],
                    "defines": ["OPENSSL_USE_NODELETE"] if self.build_config.get('shared', False) else []
                },
                "ssl": {
                    "type": "library",
                    "location": f"@prefix@/lib/libssl{lib_ext}",
                    "includes": ["@prefix@/include"],
                    "requires": ["crypto"],
                    "defines": ["OPENSSL_USE_NODELETE"] if self.build_config.get('shared', False) else []
                }
            },
            "properties": {
                "cmake_find_module_name": "OpenSSL",
                "cmake_target:crypto": "OpenSSL::Crypto",
                "cmake_target:ssl": "OpenSSL::SSL",
                "cmake_target:openssl": "OpenSSL::OpenSSL"
            }
        }

        cps_file = os.path.join(os.getcwd(), "openssl.cps")
        with open(cps_file, 'w') as f:
            json.dump(cps_data, f, indent=2)

        print(f"Generated CPS file: {cps_file}")


def main():
    """Main entry point."""
    configurer = OpenSSLConfigurer()
    sys.exit(configurer.run(sys.argv[1:]))


if __name__ == '__main__':
    main()
