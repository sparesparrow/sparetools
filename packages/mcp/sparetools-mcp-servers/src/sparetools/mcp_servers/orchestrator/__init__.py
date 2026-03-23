"""SpareTools MCP Orchestrator Server.

Chains multiple MCP servers into high-level workflows:
- run_full_ci_workflow: validate → static-analysis → report → create GitHub issue on failure
- bootstrap_new_package: create from template → add to versions.yaml → commit
- diagnose_build_failure: parse logs → call Claude → suggest fix
"""

from .server import OrchestratorServer

__all__ = ["OrchestratorServer"]
