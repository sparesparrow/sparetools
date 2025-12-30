from conan import ConanFile
from conan.tools.files import copy
import os


class SparetoolsMcpServersConan(ConanFile):
    name = "sparetools-mcp-servers"
    version = "1.0.1"
    description = "MCP (Model Context Protocol) servers for development workflows"
    license = "Apache-2.0"
    author = "SpareSparrow"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("mcp", "ai", "assistant", "automation", "development", "tools")

    # Use SpareTools foundation utilities
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    def requirements(self):
        # Require Python utilities from sparetools
        self.requires("sparetools-py/1.0.0")

    exports_sources = "src/**", "scripts/**", "config/**", "*.md", "LICENSE*"
    
    def layout(self):
        # Python package layout
        self.folders.source = "."
        self.folders.build = "build"

    def package(self):
        src_dir = os.path.join(self.source_folder, "src")
        
        # Package Python modules recursively
        copy(self, "**/*.py", 
             src=src_dir,
             dst=os.path.join(self.package_folder, "python"), 
             keep_path=True)

        # Package scripts
        scripts_dir = os.path.join(self.source_folder, "scripts")
        if os.path.exists(scripts_dir):
            copy(self, "*", 
                 src=scripts_dir,
                 dst=os.path.join(self.package_folder, "scripts"), 
                 keep_path=False)

        # Package documentation from src
        copy(self, "**/*.md", 
             src=src_dir,
             dst=os.path.join(self.package_folder, "docs"), 
             keep_path=True)
        
        # Package root README
        if os.path.exists(os.path.join(self.source_folder, "README.md")):
            copy(self, "README.md", 
                 src=self.source_folder,
                 dst=os.path.join(self.package_folder, "docs"))

        # Package config files
        config_dir = os.path.join(self.source_folder, "config")
        if os.path.exists(config_dir):
            copy(self, "*.json", 
                 src=config_dir,
                 dst=os.path.join(self.package_folder, "config"), 
                 keep_path=False)

        # Package license
        copy(self, "LICENSE*", 
             src=self.source_folder,
             dst=self.package_folder)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        # Add Python package to path
        python_path = os.path.join(self.package_folder, "python")
        self.runenv_info.append_path("PYTHONPATH", python_path)

        # Provide installation information
        self.conf_info.define("user.sparetools-mcp-servers:python_path", python_path)

    def package_id(self):
        # Make package platform-independent since it's primarily Python
        self.info.clear()
