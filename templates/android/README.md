# {{project_name}}

{{project_description}}

## Overview

This is an Android project template that leverages SpareTools packages for hermetic, cross-platform native library development. Perfect for building Android applications that require OpenSSL and other native dependencies.

## Features

- Android Studio project structure
- JNI (Java Native Interface) integration
- SpareTools OpenSSL integration
- Cross-platform native library support
- Gradle build system with Conan integration
- Comprehensive testing setup
- CI/CD pipeline ready

## Prerequisites

- Android Studio Arctic Fox or later
- Android SDK (API 21+)
- Android NDK r21+
- Conan 2.x
- Python 3.12+ (system Python for bootstrapping only)
- JDK 11+

## Quick Start

1. Clone this template:
```bash
git clone {{repository_url}}
cd {{project_name}}
```

2. Open in Android Studio:
```bash
# Open the project in Android Studio
studio.sh .
```

3. Install native dependencies:
```bash
cd app/src/main/cpp
conan install . --build=missing
```

4. Build and run:
```bash
# Build APK
./gradlew assembleDebug

# Run on device/emulator
./gradlew installDebug
```

## Project Structure

```
{{project_name}}/
├── app/                          # Main Android application module
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/{{package_name|replace('.', '/')}/
│   │   │   │   ├── MainActivity.java
│   │   │   │   └── native/
│   │   │   │       └── NativeInterface.java
│   │   │   ├── cpp/               # Native C++ code
│   │   │   │   ├── CMakeLists.txt
│   │   │   │   ├── native-lib.cpp
│   │   │   │   └── conanfile.py   # Native dependencies
│   │   │   └── res/               # Android resources
│   │   └── androidTest/           # Instrumented tests
│   └── build.gradle.kts           # App build configuration
├── gradle/wrapper/                # Gradle wrapper
├── build.gradle.kts               # Root build configuration
├── settings.gradle.kts            # Project settings
├── conanfile.py                   # Project-level dependencies
└── test_package/                  # Conan test package
```

## Native Dependencies

This project uses SpareTools packages:

- `sparetools-openssl/{{openssl_version}}` - OpenSSL library for Android
- `sparetools-cpython/{{cpython_version}}` - Python runtime (if needed)
- `sparetools-base/{{base_version}}` - Shared utilities

## Development

### Setting up Development Environment

1. **Install Android SDK/NDK:**
```bash
# Using Android Studio or command line
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"
sdkmanager "ndk;21.4.7075529"
```

2. **Configure Environment Variables:**
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_NDK_HOME=$ANDROID_HOME/ndk/21.4.7075529
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

3. **Install Dependencies:**
```bash
# Install native dependencies
cd app/src/main/cpp
conan install . --build=missing --profile android

# Install Python dependencies if any
pip install -r requirements-dev.txt
```

### Building Native Libraries

```bash
# Build for specific ABI
cd app/src/main/cpp
conan install . --build=missing -pr android-arm64

# Generate build files
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=build/Release/generators/conan_toolchain.cmake

# Build
cmake --build build --config Release
```

### Running Tests

```bash
# Unit tests (native)
cd app/src/main/cpp
ctest --build-config Release

# Instrumented tests (Android)
./gradlew connectedAndroidTest

# Unit tests (Java/Kotlin)
./gradlew test
```

### Code Quality

```bash
# Lint Kotlin/Java code
./gradlew lint

# Format code
./gradlew spotlessApply

# Static analysis
./gradlew detekt
```

## Gradle Configuration

The project uses Gradle with Conan integration:

```kotlin
// In app/build.gradle.kts
android {
    defaultConfig {
        externalNativeBuild {
            cmake {
                arguments("-DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake")
            }
        }
    }
}
```

## JNI Integration

Native code is accessed through JNI:

```java
// Java side
public class NativeInterface {
    static {
        System.loadLibrary("native-lib");
    }

    public native String getOpenSSLVersion();
    public native byte[] encryptData(byte[] data, byte[] key);
}
```

```cpp
// Native side
extern "C" JNIEXPORT jstring JNICALL
Java_{{package_name|replace('_', '_1')|replace('.', '_')}}NativeInterface_getOpenSSLVersion(
    JNIEnv* env, jobject /* this */) {
    return env->NewStringUTF(OPENSSL_VERSION_TEXT);
}
```

## Deployment

### Building Release APK

```bash
# Build signed release APK
./gradlew assembleRelease

# Build bundle for Play Store
./gradlew bundleRelease
```

### Publishing to Play Store

1. Configure signing in `app/build.gradle.kts`
2. Set up Google Play Console
3. Use Google Play Publisher Gradle plugin

## Contributing

See the main SpareTools documentation for contribution guidelines and coding standards.