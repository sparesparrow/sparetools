#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Clean Build Script
# This script cleans all build artifacts and caches

echo "=== Gamepad Mapper Clean Build ==="
echo

# Function to remove directory if it exists
remove_dir() {
    if [ -d "$1" ]; then
        echo "Removing $1..."
        rm -rf "$1"
    fi
}

# Clean build directories
echo "Cleaning build directories..."
remove_dir "build-dev"
remove_dir "build-release"
remove_dir "build"

# Clean Conan cache (optional - uncomment if you want to clean cache)
# echo "Cleaning Conan cache..."
# conan remove "*" -c

# Clean CMake cache files
echo "Cleaning CMake cache files..."
find . -name "CMakeCache.txt" -delete
find . -name "CMakeFiles" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "cmake_install.cmake" -delete
find . -name "Makefile" -delete
find . -name "*.cmake" -delete

# Clean compiled object files and executables
echo "Cleaning compiled files..."
find . -name "*.o" -delete
find . -name "*.so" -delete
find . -name "*.a" -delete
find . -name "*.exe" -delete

# Clean test artifacts
echo "Cleaning test artifacts..."
find . -name "*.gcda" -delete
find . -name "*.gcno" -delete
find . -name "*.gcov" -delete
remove_dir "test_results"

# Clean IDE files (optional)
echo "Cleaning IDE files..."
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".idea" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.swp" -delete
find . -name "*.swo" -delete

# Clean package artifacts
echo "Cleaning package artifacts..."
remove_dir "dist"
remove_dir "build_dist"
find . -name "*.tar.gz" -delete
find . -name "*.deb" -delete
find . -name "*.rpm" -delete

echo
echo "=== Clean completed successfully! ==="
echo "All build artifacts and caches have been removed."
echo
echo "To rebuild, run:"
echo "  ./scripts/build-dev.sh"