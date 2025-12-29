"""SpareTools MCP Servers Package.

This package provides MCP (Model Context Protocol) servers for various development workflows:

- ESP32 Serial Monitor: Monitor and interact with ESP32 devices
- Android Dev Tools: Build, deploy, and debug Android applications
- Conan & Cloudsmith: Package management and artifact publishing
- Repo Cleanup: Repository maintenance and cleanup operations
"""

from .esp32_serial_monitor import ESP32SerialMonitorServer as ESP32Server, app as esp32_app
from .android_dev_tools import AndroidDevToolsServer as AndroidServer, app as android_app
from .conan_cloudsmith import ConanCloudsmithServer as ConanServer, app as conan_app
from .repo_cleanup import RepoCleanupServer as RepoCleanupServer, app as repo_app

__version__ = "1.0.0"

__all__ = [
    "ESP32Server", "esp32_app",
    "AndroidServer", "android_app",
    "ConanServer", "conan_app",
    "RepoCleanupServer", "repo_app"
]