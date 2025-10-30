"""
Build orchestration utilities
"""

import os
import subprocess
from pathlib import Path


class BuildOrchestrator:
    """Orchestrates OpenSSL build processes"""
    
    def __init__(self):
        self.build_dir = Path.cwd() / "build"
        self.build_dir.mkdir(exist_ok=True)
    
    def configure(self, options=None):
        """Configure OpenSSL build"""
        cmd = ["python3", "configure.py"]
        if options:
            cmd.extend(options)
        
        result = subprocess.run(cmd, cwd=self.build_dir)
        return result.returncode == 0
    
    def build(self, jobs=None):
        """Build OpenSSL"""
        cmd = ["make"]
        if jobs:
            cmd.extend(["-j", str(jobs)])
        
        result = subprocess.run(cmd, cwd=self.build_dir)
        return result.returncode == 0


# Global instance
build_orchestrator = BuildOrchestrator()