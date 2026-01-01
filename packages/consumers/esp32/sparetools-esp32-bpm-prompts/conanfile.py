#!/usr/bin/env python3
"""
SpareTools ESP32 BPM Detector Prompts Package
Aggregates ESP32-specific prompts from mcp-prompts for esp32-bpm-detector project
"""

import os
import json
from pathlib import Path
from conan import ConanFile
from conan.tools.files import copy, save, load
from conan.tools.scm import Git


class SpareToolsESP32BpmPromptsConan(ConanFile):
    name = "sparetools-esp32-bpm-prompts"
    version = "1.0.0"
    license = "MIT"
    author = "sparesparrow"
    url = "https://github.com/sparesparrow/sparetools"
    description = "Aggregated ESP32 BPM detector development prompts from mcp-prompts with SpareTools integration"
    topics = ("esp32", "bpm", "prompts", "embedded", "mcp", "development")

    # Use SpareTools foundation
    python_requires = "sparetools-base/2.0.3"

    # Depend on mcp-prompts package
    requires = "sparetools-mcp-prompts/3.12.5"

    settings = None
    package_type = "application"

    def source(self):
        """Fetch prompts from mcp-prompts GitHub repo"""
        git = Git(self)
        repo_url = "https://github.com/sparesparrow/mcp-prompts.git"
        tag = "v3.12.5"
        
        self.output.info(f"Fetching ESP32 prompts from mcp-prompts (tag: {tag})...")
        git.clone(repo_url, target="mcp-prompts")
        git.checkout(tag, cwd="mcp-prompts")

    def package(self):
        """Package ESP32-specific prompts and create aggregated index"""
        mcp_prompts_dir = os.path.join(self.source_folder, "mcp-prompts", "data", "prompts")
        
        # Copy ESP32 prompts
        esp32_prompts = [
            "esp32/esp32-network-ap-mode-configuration.json",
            "esp32/esp32-platformio-serial-upload-debugging.json",
            "esp32/esp32-flatbuffers-schema-sync-workflow.json",
            "esp32/esp32-mcp-server-http-api-integration.json",
            "esp32/embedded-esp32-full-bringup-workflow.json",
            "esp32/esp32-fft-configuration-guide.json",
            "esp32/esp32-fft-optimization-methodology.json",
        ]
        
        # Copy embedded prompts
        embedded_prompts = [
            "embedded/embedded-audio-fft-memory-constraints.json",
            "embedded/device-detection.json",
            "embedded/firmware-deployment.json",
            "embedded/jtag-workflow.json",
            "embedded/serial-debugging.json",
        ]
        
        # Copy MCP development prompts
        mcp_prompts = [
            "mcp-development/mcp-server-file-storage-index-sync.json",
        ]
        
        prompts_dir = os.path.join(self.package_folder, "prompts")
        os.makedirs(prompts_dir, exist_ok=True)
        
        all_prompts = []
        
        # Copy and collect ESP32 prompts
        for prompt_path in esp32_prompts:
            src = os.path.join(mcp_prompts_dir, prompt_path)
            if os.path.exists(src):
                dst_dir = os.path.join(prompts_dir, os.path.dirname(prompt_path))
                os.makedirs(dst_dir, exist_ok=True)
                copy(self, os.path.basename(prompt_path), src=os.path.dirname(src), dst=dst_dir)
                
                # Load prompt data for index
                with open(src, 'r') as f:
                    prompt_data = json.load(f)
                    all_prompts.append({
                        'id': prompt_data.get('id'),
                        'name': prompt_data.get('name'),
                        'description': prompt_data.get('description'),
                        'tags': prompt_data.get('tags', []),
                        'category': 'esp32'
                    })
        
        # Copy embedded prompts
        for prompt_path in embedded_prompts:
            src = os.path.join(mcp_prompts_dir, prompt_path)
            if os.path.exists(src):
                dst_dir = os.path.join(prompts_dir, os.path.dirname(prompt_path))
                os.makedirs(dst_dir, exist_ok=True)
                copy(self, os.path.basename(prompt_path), src=os.path.dirname(src), dst=dst_dir)
                
                with open(src, 'r') as f:
                    prompt_data = json.load(f)
                    all_prompts.append({
                        'id': prompt_data.get('id'),
                        'name': prompt_data.get('name'),
                        'description': prompt_data.get('description'),
                        'tags': prompt_data.get('tags', []),
                        'category': 'embedded'
                    })
        
        # Copy MCP development prompts
        for prompt_path in mcp_prompts:
            src = os.path.join(mcp_prompts_dir, prompt_path)
            if os.path.exists(src):
                dst_dir = os.path.join(prompts_dir, os.path.dirname(prompt_path))
                os.makedirs(dst_dir, exist_ok=True)
                copy(self, os.path.basename(prompt_path), src=os.path.dirname(src), dst=dst_dir)
                
                with open(src, 'r') as f:
                    prompt_data = json.load(f)
                    all_prompts.append({
                        'id': prompt_data.get('id'),
                        'name': prompt_data.get('name'),
                        'description': prompt_data.get('description'),
                        'tags': prompt_data.get('tags', []),
                        'category': 'mcp-development'
                    })
        
        # Create aggregated index
        index_data = {
            'prompts': all_prompts,
            'metadata': {
                'totalPrompts': len(all_prompts),
                'package': self.name,
                'version': self.version,
                'source': 'mcp-prompts@3.12.5',
                'description': 'ESP32 BPM detector specific prompts aggregated from mcp-prompts'
            }
        }
        
        index_path = os.path.join(prompts_dir, "index.json")
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        self.output.info(f"Packaged {len(all_prompts)} ESP32 BPM detector prompts")

    def package_info(self):
        """Configure package environment"""
        prompts_dir = os.path.join(self.package_folder, "prompts")
        
        # Set environment variables
        self.runenv_info.define("SPARETOOLS_ESP32_BPM_PROMPTS_DIR", prompts_dir)
        self.runenv_info.define("SPARETOOLS_ESP32_BPM_PROMPTS_INDEX", os.path.join(prompts_dir, "index.json"))
        
        # Make prompts available to MCP servers
        self.runenv_info.define("MCP_PROMPTS_PATH", prompts_dir)