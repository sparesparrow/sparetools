"""Claude-powered security analysis tools."""

from ..client import AnthropicClient


_SECURITY_SYSTEM = """You are a security engineer specializing in:
- C++ and Python vulnerability analysis
- Embedded systems security (ESP32, FIPS 140-3)
- OWASP Top 10 and CWE classification
- CVE analysis and patch recommendations
- Supply chain security (SBOM, Trivy findings)
Provide severity ratings (CRITICAL/HIGH/MEDIUM/LOW), CVE references where applicable,
and concrete remediation steps."""


def analyze_vulnerability(
    trivy_output: str, package_name: str = "", client: AnthropicClient = None
) -> str:
    """Interpret Trivy scan output and prioritize remediation."""
    c = client or AnthropicClient()
    pkg_ctx = f" for package '{package_name}'" if package_name else ""
    return c.ask(
        system=_SECURITY_SYSTEM,
        user=(
            f"Analyze these Trivy vulnerability findings{pkg_ctx}. "
            "Prioritize by exploitability and suggest fixes:\n\n"
            f"```\n{trivy_output}\n```"
        ),
    )


def suggest_fix(
    vulnerability_description: str,
    affected_code: str = "",
    client: AnthropicClient = None,
) -> str:
    """Suggest a fix for a described security vulnerability."""
    c = client or AnthropicClient()
    code_section = f"\n\nAffected code:\n```\n{affected_code}\n```" if affected_code else ""
    return c.ask(
        system=_SECURITY_SYSTEM,
        user=f"Suggest a fix for this vulnerability:{code_section}\n\n{vulnerability_description}",
    )


def review_secrets_exposure(file_content: str, filename: str = "", client: AnthropicClient = None) -> str:
    """Check a file for potential secrets or credential exposure."""
    c = client or AnthropicClient()
    file_ctx = f" ({filename})" if filename else ""
    return c.ask(
        system=_SECURITY_SYSTEM,
        user=(
            f"Review this file{file_ctx} for exposed secrets, credentials, or sensitive data. "
            "Identify specific lines and recommend remediation:\n\n"
            f"```\n{file_content}\n```"
        ),
    )
