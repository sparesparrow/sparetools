"""Claude-powered Conan recipe and package management advisor."""

from ..client import AnthropicClient


_CONAN_SYSTEM = """You are a Conan 2.x expert. You know the SpareTools monorepo conventions:
- python_requires = "sparetools-base/2.0.4" for recipe sharing (not 'requires')
- 5-layer architecture: Foundation → Prebuilt Tools → Utilities → Orchestration → Consumers
- All versions defined in /versions.yaml
- Security gates (Trivy, Syft) run in build()
- Package types: python-require, application, library, header-library
Provide specific, actionable recommendations."""


def audit_recipe(conanfile_content: str, client: AnthropicClient = None) -> str:
    """Audit a conanfile.py and suggest improvements."""
    c = client or AnthropicClient()
    return c.ask(
        system=_CONAN_SYSTEM,
        user=f"Audit this conanfile.py and identify issues or improvements:\n\n```python\n{conanfile_content}\n```",
    )


def suggest_package_version(
    package_name: str,
    current_version: str,
    changelog: str = "",
    client: AnthropicClient = None,
) -> str:
    """Suggest the next semantic version for a package."""
    c = client or AnthropicClient()
    ctx = f"Changelog:\n{changelog}" if changelog else "No changelog provided."
    return c.ask(
        system=_CONAN_SYSTEM,
        user=(
            f"Package: {package_name}, current version: {current_version}\n"
            f"{ctx}\n\n"
            "Suggest the next semantic version (MAJOR.MINOR.PATCH) and explain why."
        ),
    )


def diagnose_build_failure(
    build_log: str, conanfile_content: str = "", client: AnthropicClient = None
) -> str:
    """Diagnose a Conan build failure and suggest a fix."""
    c = client or AnthropicClient()
    recipe_section = f"\nconanfile.py:\n```python\n{conanfile_content}\n```" if conanfile_content else ""
    return c.ask(
        system=_CONAN_SYSTEM,
        user=f"Diagnose this Conan build failure and provide a fix:{recipe_section}\n\nBuild log:\n```\n{build_log}\n```",
    )
