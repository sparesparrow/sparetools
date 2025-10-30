from conan import ConanFile
from conan.tools.files import copy

class SpareToolsMCPOrchestratorConan(ConanFile):
    name = "sparetools-mcp-orchestrator"
    version = "1.0.0"
    package_type = "python-require"
    description = "MCP project orchestrator for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    exports_sources = "mcp_project_orchestrator/**", "scripts/**"
    
    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "*.sh", src=self.source_folder, dst=self.package_folder, keep_path=True)
    
    def package_info(self):
        self.cpp_info.libs = []
        self.env_info.PYTHONPATH.append(self.package_folder)
