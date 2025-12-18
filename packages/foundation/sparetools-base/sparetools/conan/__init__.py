"""
Conan Management Module

Provides utilities for Conan package management, remote configuration,
profile validation, cache operations, and command-line launcher.
"""

from .core import (
    get_default_conan,
    get_conan_home,
    get_all_packages_in_cache,
    remove_conan_package_in_cache,
    ConanConfiguration,
    ConanJsonLoader,
    ConanConfigurationTracker,
    download_python_interpreter,
    print_package_version,
    print_package_path,
    install_packages_for_repository,
    download_package_for_repository,
    get_info_about_package,
    create_package_graph,
    install_package_version,
    download_package_version,
    reinitialize_conan_cache,
    remove_conan_lock_files,
    get_all_package_config_folders,
    get_configuration_safe,
    setup_parallel_download,
)

from .repositories import (
    RepositoryType,
    RepositoryConfig,
    RepositoryManager,
    setup_cloudsmith_repository,
    setup_github_repository,
    setup_generic_conan_remote,
    enable_conan_remote,
    disable_conan_remote,
    remove_conan_remote,
)

from .config import (
    ConanRepositoryConfig,
    create_config_template,
    load_repositories_from_config,
)

from . import launcher

__all__ = [
    # Core functions
    "get_default_conan",
    "get_conan_home",
    "get_all_packages_in_cache",
    "remove_conan_package_in_cache",
    "ConanConfiguration",
    "ConanJsonLoader",
    "ConanConfigurationTracker",

    # Extended functions
    "download_python_interpreter",
    "print_package_version",
    "print_package_path",
    "install_packages_for_repository",
    "download_package_for_repository",
    "get_info_about_package",
    "create_package_graph",
    "install_package_version",
    "download_package_version",
    "reinitialize_conan_cache",
    "remove_conan_lock_files",
    "get_all_package_config_folders",
    "get_configuration_safe",
    "setup_parallel_download",

    # Repository management
    "RepositoryType",
    "RepositoryConfig",
    "RepositoryManager",
    "setup_cloudsmith_repository",
    "setup_github_repository",
    "setup_generic_conan_remote",
    "enable_conan_remote",
    "disable_conan_remote",
    "remove_conan_remote",

    # Configuration
    "ConanRepositoryConfig",
    "create_config_template",
    "load_repositories_from_config",

    # Launcher module
    "launcher",
]