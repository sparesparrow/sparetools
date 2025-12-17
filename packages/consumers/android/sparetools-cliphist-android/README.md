# SpareTools ClipHist Android

ClipHist Android is a secure clipboard history manager for Android devices, built as part of the SpareTools ecosystem.

## Features

- **Secure Clipboard History**: Encrypted storage of clipboard history using SQLCipher
- **Modern Android Architecture**: Built with Jetpack Compose, Hilt, and Room
- **Privacy-First**: No data collection or external services required
- **Material Design 3**: Modern, accessible UI following Android design guidelines

## Architecture

This consumer package integrates with the SpareTools foundation layer:

- **Foundation Dependencies**: `sparetools-base`, `sparetools-recipe-base`
- **Security**: SQLCipher for encrypted database storage
- **UI Framework**: Jetpack Compose with Material 3
- **Dependency Injection**: Hilt for clean architecture
- **Database**: Room with SQLCipher encryption

## Building

This package requires Android development tools:

```bash
# Install required tools via Conan
conan install . --build missing

# Build APK
conan build .
```

## Android Requirements

- **minSdk**: 21 (Android 5.0)
- **targetSdk**: 34 (Android 14)
- **compileSdk**: 34

## Security Considerations

- All clipboard data is encrypted using SQLCipher
- No internet permissions required for core functionality
- Secure key management for encryption
- Android's permission model for clipboard access

## Development

### Project Structure

```
sparetools-cliphist-android/
├── app/
│   ├── build.gradle.kts          # App configuration
│   └── src/main/
│       ├── AndroidManifest.xml   # App permissions and components
│       ├── java/com/sparesparrow/cliphist/
│       │   ├── ClipHistApplication.kt  # Hilt application class
│       │   └── ui/
│       │       ├── MainActivity.kt     # Main activity
│       │       └── theme/              # Compose theme
│       └── res/                        # Android resources
├── build.gradle.kts               # Root build configuration
├── settings.gradle.kts            # Project settings
└── conanfile.py                   # Conan package definition
```

### Key Components

- **MainActivity**: Entry point with Compose UI
- **ClipboardMonitorService**: Background service for clipboard monitoring
- **Room Database**: Encrypted local storage
- **Hilt Modules**: Dependency injection configuration

## Integration with SpareTools

This Android consumer demonstrates the SpareTools layered architecture:

1. **Foundation Layer**: Core utilities and shared components
2. **Consumer Layer**: Platform-specific applications (Android)
3. **Shared Scripts**: Build and deployment automation
4. **CI/CD**: Cross-platform testing and deployment

## Testing

```bash
# Unit tests
./gradlew test

# Instrumentation tests
./gradlew connectedAndroidTest

# Integration with SpareTools CI
conan test . --profile android
```