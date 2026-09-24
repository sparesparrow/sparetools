"""Claude-powered code review and explanation tools."""

from ..client import AnthropicClient


_REVIEW_SYSTEM = """You are a senior C++/Python engineer specializing in Conan 2.x packages,
embedded systems (ESP32, FreeRTOS), and MCP server development. Review code for:
- Correctness and edge cases
- Security vulnerabilities (OWASP Top 10, memory safety)
- SpareTools conventions (python_requires, security gates, SBOM)
- Performance and maintainability
Be specific: cite line numbers when possible, suggest concrete fixes."""


def review_code(code: str, language: str = "python", client: AnthropicClient = None) -> str:
    """Review a code snippet and return structured feedback."""
    c = client or AnthropicClient()
    return c.ask(
        system=_REVIEW_SYSTEM,
        user=f"Review this {language} code:\n\n```{language}\n{code}\n```",
    )


def explain_error(error_output: str, context: str = "", client: AnthropicClient = None) -> str:
    """Explain a build/test error and suggest a fix."""
    c = client or AnthropicClient()
    ctx_section = f"\n\nContext:\n{context}" if context else ""
    return c.ask(
        system=_REVIEW_SYSTEM,
        user=f"Explain this error and provide a fix:{ctx_section}\n\n```\n{error_output}\n```",
    )


def explain_code(code: str, language: str = "python", client: AnthropicClient = None) -> str:
    """Explain what a code snippet does in plain language."""
    c = client or AnthropicClient()
    return c.ask(
        system="You are a senior software engineer. Explain code clearly and concisely.",
        user=f"Explain this {language} code:\n\n```{language}\n{code}\n```",
    )
