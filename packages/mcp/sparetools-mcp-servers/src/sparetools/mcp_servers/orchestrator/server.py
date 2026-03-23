"""MCP Orchestrator Server — chains SpareTools workflows end-to-end."""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from mcp.server.fastmcp import FastMCP
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    logger.warning("mcp package not available — server will not start")


def _run(cmd: List[str], cwd: Optional[str] = None, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, check=check)


def _repo_root() -> str:
    result = _run(["git", "rev-parse", "--show-toplevel"])
    return result.stdout.strip() if result.returncode == 0 else os.getcwd()


class OrchestratorServer:
    """High-level workflow orchestrator across all SpareTools MCP servers."""

    def __init__(self):
        self._root = _repo_root()
        self._anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self._github_token = os.environ.get("GITHUB_TOKEN", "")
        self._cloudsmith_key = os.environ.get("CLOUDSMITH_API_KEY", "")

    # ------------------------------------------------------------------
    # Public workflow tools
    # ------------------------------------------------------------------

    def run_full_ci_workflow(self, package_path: str) -> Dict[str, Any]:
        """Run validate → static-analysis → report for a package.

        Steps:
        1. conan inspect (validate conanfile.py)
        2. Run flake8/black on Python source
        3. Run pytest if test_package/ exists
        4. Return structured report

        Args:
            package_path: Relative path to the package directory (e.g. 'packages/mcp/sparetools-mcp-core').

        Returns:
            Dict with keys: passed (bool), steps (list), summary (str).
        """
        abs_path = str(Path(self._root) / package_path)
        steps: List[Dict[str, Any]] = []
        passed = True

        # Step 1: conan inspect
        result = _run(["conan", "inspect", abs_path], cwd=self._root)
        step = {
            "name": "conan_inspect",
            "returncode": result.returncode,
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:500],
        }
        steps.append(step)
        if result.returncode != 0:
            passed = False

        # Step 2: flake8 on src/
        src_dir = str(Path(abs_path) / "src")
        if Path(src_dir).exists():
            result = _run(["python3", "-m", "flake8", src_dir, "--max-line-length=120"], cwd=self._root)
            step = {
                "name": "flake8",
                "returncode": result.returncode,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500],
            }
            steps.append(step)
            if result.returncode != 0:
                passed = False

        # Step 3: pytest test_package/ if present
        test_dir = str(Path(abs_path) / "test_package")
        if Path(test_dir).exists():
            result = _run(["python3", "-m", "pytest", test_dir, "-v", "--tb=short"], cwd=self._root)
            step = {
                "name": "pytest",
                "returncode": result.returncode,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500],
            }
            steps.append(step)
            if result.returncode != 0:
                passed = False

        summary = f"{'PASSED' if passed else 'FAILED'}: {len(steps)} steps, {sum(1 for s in steps if s['returncode'] != 0)} failures"
        return {"passed": passed, "steps": steps, "summary": summary, "package_path": package_path}

    def bootstrap_new_package(
        self,
        name: str,
        category: str,
        version: str = "1.0.0",
        package_type: str = "python-require",
        description: str = "",
    ) -> Dict[str, Any]:
        """Scaffold a new SpareTools package from template.

        Creates the directory structure, conanfile.py, and registers
        the package in versions.yaml.

        Args:
            name: Package name without 'sparetools-' prefix (e.g. 'my-tool').
            category: Target category directory (e.g. 'mcp', 'foundation', 'security').
            version: Initial semantic version.
            package_type: Conan package type ('python-require', 'application', 'library').
            description: Short package description.

        Returns:
            Dict with created_files list and versions_yaml_updated bool.
        """
        full_name = f"sparetools-{name}"
        pkg_dir = Path(self._root) / "packages" / category / full_name
        created: List[str] = []

        # Create directory structure
        for subdir in ["src", "test_package"]:
            (pkg_dir / subdir).mkdir(parents=True, exist_ok=True)

        # Write conanfile.py
        conanfile_content = f'''from conan import ConanFile
from conan.tools.files import copy
import os


class {_to_class_name(full_name)}Conan(ConanFile):
    name = "{full_name}"
    version = "{version}"
    description = "{description or f'SpareTools {name} package'}"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("{name}",)

    python_requires = "sparetools-base/2.0.4"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"
    tool_requires = "sparetools-cpython/3.12.7"

    package_type = "{package_type}"

    exports_sources = "src/**/*.py", "README.md"

    def package(self):
        copy(self, "*.py",
             src=os.path.join(self.source_folder, "src"),
             dst=os.path.join(self.package_folder, "python"))

    def package_info(self):
        self.runenv_info.append_path(
            "PYTHONPATH", os.path.join(self.package_folder, "python"))
'''
        conanfile_path = pkg_dir / "conanfile.py"
        conanfile_path.write_text(conanfile_content)
        created.append(str(conanfile_path.relative_to(self._root)))

        # Write minimal src/__init__.py
        init_dir = pkg_dir / "src" / "sparetools" / name.replace("-", "_")
        init_dir.mkdir(parents=True, exist_ok=True)
        (init_dir / "__init__.py").write_text(f'"""{full_name} package."""\n\n__version__ = "{version}"\n')
        created.append(str((init_dir / "__init__.py").relative_to(self._root)))

        # Register in versions.yaml
        versions_file = Path(self._root) / "versions.yaml"
        versions_updated = False
        if versions_file.exists():
            try:
                import yaml
                with open(versions_file) as f:
                    data = yaml.safe_load(f) or {}
                data.setdefault(category, {})[name] = version
                with open(versions_file, "w") as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                versions_updated = True
            except Exception as e:
                logger.warning("Could not update versions.yaml: %s", e)

        return {
            "package_dir": str(pkg_dir.relative_to(self._root)),
            "created_files": created,
            "versions_yaml_updated": versions_updated,
        }

    def diagnose_build_failure(
        self, build_log: str, package_path: str = ""
    ) -> Dict[str, Any]:
        """Parse a build failure log and suggest a fix.

        If ANTHROPIC_API_KEY is set, uses Claude for deeper analysis.
        Otherwise returns a structured heuristic diagnosis.

        Args:
            build_log: Raw build/test log output.
            package_path: Optional path to the package conanfile.py.

        Returns:
            Dict with diagnosis (str), suggestions (list[str]), ai_assisted (bool).
        """
        suggestions: List[str] = []
        diagnosis = "Build failure detected."
        ai_assisted = False

        # Heuristic checks
        if "Missing python_requires" in build_log or "python_requires" in build_log:
            suggestions.append("Build foundation packages first: conan create packages/foundation/sparetools-base --version=2.0.4 --build=missing")
        if "ImportError" in build_log or "ModuleNotFoundError" in build_log:
            suggestions.append("Install missing Python dependencies: check requirements.txt in the package directory.")
        if "Permission denied" in build_log:
            suggestions.append("Check file permissions and ensure build directories are writable.")
        if "No such file or directory" in build_log:
            suggestions.append("Verify that exports_sources in conanfile.py matches the actual source layout.")
        if "conan remote" in build_log.lower() or "not found" in build_log.lower():
            suggestions.append("Add Cloudsmith remote: conan remote add sparesparrow-conan https://dl.cloudsmith.io/public/sparesparrow-conan/sparetools/")

        # AI-assisted analysis if key available
        if self._anthropic_key:
            try:
                from sparetools.mcp_anthropic.tools.conan_advisor import diagnose_build_failure as ai_diagnose
                conanfile_content = ""
                if package_path:
                    cf = Path(self._root) / package_path / "conanfile.py"
                    if cf.exists():
                        conanfile_content = cf.read_text()
                ai_result = ai_diagnose(build_log, conanfile_content)
                diagnosis = ai_result
                ai_assisted = True
            except Exception as e:
                logger.warning("AI diagnosis unavailable: %s", e)
                diagnosis = f"Heuristic diagnosis only (AI unavailable: {e}). See suggestions."

        return {
            "diagnosis": diagnosis,
            "suggestions": suggestions,
            "ai_assisted": ai_assisted,
            "log_excerpt": build_log[-1000:] if len(build_log) > 1000 else build_log,
        }


def _to_class_name(package_name: str) -> str:
    """Convert 'sparetools-my-tool' to 'SparetoolsMyTool'."""
    return "".join(part.capitalize() for part in package_name.replace("-", " ").split())


def create_server() -> Any:
    """Create and configure the FastMCP orchestrator server."""
    if not _MCP_AVAILABLE:
        raise RuntimeError("mcp package required: pip install mcp>=1.0.0")

    mcp = FastMCP("sparetools-orchestrator")
    orch = OrchestratorServer()

    @mcp.tool()
    def run_full_ci_workflow(package_path: str) -> Dict[str, Any]:
        """Run the full CI workflow (validate + lint + test) for a package.

        Args:
            package_path: Relative path to the package (e.g. 'packages/mcp/sparetools-mcp-core').
        """
        return orch.run_full_ci_workflow(package_path)

    @mcp.tool()
    def bootstrap_new_package(
        name: str,
        category: str,
        version: str = "1.0.0",
        package_type: str = "python-require",
        description: str = "",
    ) -> Dict[str, Any]:
        """Scaffold a new SpareTools Conan package with standard structure.

        Args:
            name: Package name without 'sparetools-' prefix.
            category: Target category (e.g. 'mcp', 'foundation', 'security').
            version: Initial semantic version string.
            package_type: Conan package type.
            description: Short package description.
        """
        return orch.bootstrap_new_package(name, category, version, package_type, description)

    @mcp.tool()
    def diagnose_build_failure(build_log: str, package_path: str = "") -> Dict[str, Any]:
        """Diagnose a Conan build/test failure and suggest fixes.

        Uses Claude AI if ANTHROPIC_API_KEY is set, otherwise heuristic analysis.

        Args:
            build_log: Raw build or test log output.
            package_path: Optional relative path to the package directory.
        """
        return orch.diagnose_build_failure(build_log, package_path)

    return mcp


if __name__ == "__main__":
    server = create_server()
    server.run()
