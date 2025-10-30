#!/usr/bin/env python3
"""
Cache optimization script for OpenSSL Conan packages
Implements intelligent cache key strategies and optimization
"""

import os
import sys
import json
import yaml
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse


class CacheOptimizer:
    """Cache optimization for OpenSSL Conan packages"""
    
    def __init__(self, config_file: str = "conan-dev/cache-optimization.yml"):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load cache optimization configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default cache optimization configuration"""
        return {
            'cache': {
                'levels': [
                    {'name': 'local', 'type': 'filesystem', 'path': '${CONAN_USER_HOME}/.conan2/cache'},
                    {'name': 'shared', 'type': 'filesystem', 'path': '/shared/conan-cache'},
                    {'name': 'remote', 'type': 'conan_remote', 'remote': 'artifactory'}
                ],
                'key_strategies': {
                    'source': {
                        'include': ['conanfile.py', 'VERSION.dat', 'configure', 'config'],
                        'exclude': ['test/**', 'fuzz/**', 'demos/**', 'doc/**']
                    },
                    'binary': {
                        'include': ['settings.os', 'settings.arch', 'settings.compiler', 'options.fips'],
                        'exclude': ['options.openssldir', 'options.cafile', 'options.capath']
                    }
                }
            }
        }
    
    def optimize_cache_keys(self) -> Dict[str, str]:
        """Generate optimized cache keys"""
        print("🔑 Generating optimized cache keys...")
        
        cache_keys = {}
        
        # Source cache key
        source_key = self._generate_source_cache_key()
        cache_keys['source'] = source_key
        
        # Binary cache key
        binary_key = self._generate_binary_cache_key()
        cache_keys['binary'] = binary_key
        
        # Combined cache key
        combined_key = self._generate_combined_cache_key(source_key, binary_key)
        cache_keys['combined'] = combined_key
        
        print(f"✓ Source cache key: {source_key[:16]}...")
        print(f"✓ Binary cache key: {binary_key[:16]}...")
        print(f"✓ Combined cache key: {combined_key[:16]}...")
        
        return cache_keys
    
    def _generate_source_cache_key(self) -> str:
        """Generate source code cache key"""
        key_parts = []
        
        # Include important source files
        include_files = self.config['cache']['key_strategies']['source']['include']
        for file_pattern in include_files:
            if '*' in file_pattern:
                # Handle glob patterns
                import glob
                files = glob.glob(file_pattern)
            else:
                files = [file_pattern] if os.path.exists(file_pattern) else []
            
            for file_path in files:
                if os.path.exists(file_path):
                    file_hash = self._calculate_file_hash(file_path)
                    if file_hash:
                        key_parts.append(f"{file_path}:{file_hash[:8]}")
        
        # Sort for consistent ordering
        key_parts.sort()
        
        # Generate final hash
        combined_content = '|'.join(key_parts)
        return hashlib.sha256(combined_content.encode()).hexdigest()
    
    def _generate_binary_cache_key(self) -> str:
        """Generate binary cache key based on settings and options"""
        key_parts = []
        
        # Get Conan settings
        try:
            result = subprocess.run(['conan', 'profile', 'show', 'default'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                profile_content = result.stdout
                # Extract key settings
                settings = self._extract_settings_from_profile(profile_content)
                key_parts.extend(settings)
        except Exception as e:
            print(f"Warning: Could not get Conan profile: {e}")
        
        # Add OpenSSL-specific options
        openssl_options = [
            'fips', 'shared', 'no_asm', 'enable_quic', 'enable_zlib', 
            'enable_zstd', 'enable_brotli', 'no_deprecated'
        ]
        
        for option in openssl_options:
            # This would need to be passed from the build context
            # For now, we'll use a placeholder
            key_parts.append(f"option.{option}:default")
        
        # Generate final hash
        combined_content = '|'.join(key_parts)
        return hashlib.sha256(combined_content.encode()).hexdigest()
    
    def _extract_settings_from_profile(self, profile_content: str) -> List[str]:
        """Extract settings from Conan profile content"""
        settings = []
        lines = profile_content.split('\n')
        
        in_settings = False
        for line in lines:
            line = line.strip()
            if line == '[settings]':
                in_settings = True
                continue
            elif line.startswith('[') and line != '[settings]':
                in_settings = False
                continue
            
            if in_settings and '=' in line:
                settings.append(line)
        
        return settings
    
    def _generate_combined_cache_key(self, source_key: str, binary_key: str) -> str:
        """Generate combined cache key"""
        combined_content = f"source:{source_key}|binary:{binary_key}"
        return hashlib.sha256(combined_content.encode()).hexdigest()
    
    def _calculate_file_hash(self, file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """Calculate hash of a file"""
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            print(f"Warning: Could not calculate hash for {file_path}: {e}")
            return None
    
    def setup_compiler_cache(self):
        """Set up compiler cache (CCache/SCCache)"""
        print("🔧 Setting up compiler cache...")
        
        ccache_config = self.config.get('compiler_cache', {}).get('ccache', {})
        if ccache_config.get('enabled', False):
            self._setup_ccache(ccache_config)
        
        sccache_config = self.config.get('compiler_cache', {}).get('sccache', {})
        if sccache_config.get('enabled', False):
            self._setup_sccache(sccache_config)
    
    def _setup_ccache(self, config: Dict):
        """Set up CCache configuration"""
        try:
            # Check if CCache is available
            result = subprocess.run(['ccache', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("Warning: CCache not available")
                return
            
            # Configure CCache
            ccache_dir = config.get('directory', '/cache/ccache')
            os.makedirs(ccache_dir, exist_ok=True)
            
            # Set environment variables
            os.environ['CCACHE_DIR'] = ccache_dir
            os.environ['CCACHE_MAXSIZE'] = config.get('max_size', '5GB')
            os.environ['CCACHE_COMPRESS'] = str(config.get('compress', True)).lower()
            os.environ['CCACHE_COMPRESSLEVEL'] = str(config.get('compress_level', 6))
            os.environ['CCACHE_HASHDIR'] = str(config.get('hash_dir', True)).lower()
            
            # Set sloppiness
            sloppiness = config.get('sloppiness', 'file_macro,time_macros,include_file_mtime')
            os.environ['CCACHE_SLOPPINESS'] = sloppiness
            
            print(f"✓ CCache configured: {ccache_dir}")
            
        except Exception as e:
            print(f"Warning: Could not set up CCache: {e}")
    
    def _setup_sccache(self, config: Dict):
        """Set up SCCache configuration"""
        try:
            # Check if SCCache is available
            result = subprocess.run(['sccache', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("Warning: SCCache not available")
                return
            
            # Configure SCCache
            sccache_dir = config.get('directory', '/cache/sccache')
            os.makedirs(sccache_dir, exist_ok=True)
            
            # Set environment variables
            os.environ['SCCACHE_DIR'] = sccache_dir
            os.environ['SCCACHE_MAXSIZE'] = config.get('max_size', '5GB')
            os.environ['SCCACHE_COMPRESSION'] = config.get('compression', 'zstd')
            
            print(f"✓ SCCache configured: {sccache_dir}")
            
        except Exception as e:
            print(f"Warning: Could not set up SCCache: {e}")
    
    def optimize_build_parallelization(self):
        """Optimize build parallelization settings"""
        print("⚡ Optimizing build parallelization...")
        
        build_config = self.config.get('build_cache', {}).get('parallel', {})
        max_jobs = build_config.get('max_jobs', 8)
        job_multiplier = build_config.get('job_multiplier', 1.5)
        
        # Calculate optimal job count
        try:
            cpu_count = os.cpu_count() or 1
            optimal_jobs = min(int(cpu_count * job_multiplier), max_jobs)
            
            # Set environment variables
            os.environ['CONAN_CPU_COUNT'] = str(optimal_jobs)
            os.environ['MAKEFLAGS'] = f'-j{optimal_jobs}'
            
            print(f"✓ Optimal parallel jobs: {optimal_jobs} (CPU cores: {cpu_count})")
            
        except Exception as e:
            print(f"Warning: Could not optimize parallelization: {e}")
    
    def setup_remote_cache(self):
        """Set up remote cache configuration"""
        print("🌐 Setting up remote cache...")
        
        remote_config = self.config.get('remote_cache', {})
        
        for remote_name, config in remote_config.items():
            if config.get('enabled', False):
                self._setup_remote_cache(remote_name, config)
    
    def _setup_remote_cache(self, remote_name: str, config: Dict):
        """Set up a specific remote cache"""
        try:
            remote = config.get('remote', remote_name)
            cache_ttl = config.get('cache_ttl', '7d')
            max_versions = config.get('max_versions', 10)
            
            # Set cache TTL
            os.environ[f'CONAN_CACHE_TTL_{remote.upper()}'] = cache_ttl
            os.environ[f'CONAN_MAX_VERSIONS_{remote.upper()}'] = str(max_versions)
            
            print(f"✓ Remote cache configured: {remote_name}")
            
        except Exception as e:
            print(f"Warning: Could not set up remote cache {remote_name}: {e}")
    
    def cleanup_cache(self):
        """Clean up old cache entries"""
        print("🧹 Cleaning up cache...")
        
        cleanup_config = self.config.get('cleanup', {})
        if not cleanup_config.get('automatic', {}).get('enabled', False):
            return
        
        try:
            # Clean Conan cache
            subprocess.run(['conan', 'cache', 'clean', '--all'], check=False)
            print("✓ Conan cache cleaned")
            
            # Clean compiler cache if configured
            ccache_config = self.config.get('compiler_cache', {}).get('ccache', {})
            if ccache_config.get('enabled', False):
                subprocess.run(['ccache', '-C'], check=False)
                print("✓ CCache cleaned")
            
        except Exception as e:
            print(f"Warning: Could not clean cache: {e}")
    
    def generate_cache_report(self) -> Dict:
        """Generate cache performance report"""
        print("📊 Generating cache report...")
        
        report = {
            'timestamp': str(os.environ.get('SOURCE_DATE_EPOCH', '')),
            'cache_keys': self.optimize_cache_keys(),
            'environment': {
                'CONAN_CPU_COUNT': os.environ.get('CONAN_CPU_COUNT', ''),
                'CCACHE_DIR': os.environ.get('CCACHE_DIR', ''),
                'SCCACHE_DIR': os.environ.get('SCCACHE_DIR', '')
            },
            'performance': self._get_cache_performance()
        }
        
        # Save report
        report_file = 'cache-performance-report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Cache report saved: {report_file}")
        return report
    
    def _get_cache_performance(self) -> Dict:
        """Get cache performance metrics"""
        performance = {}
        
        # Get CCache stats
        try:
            result = subprocess.run(['ccache', '-s'], capture_output=True, text=True)
            if result.returncode == 0:
                performance['ccache'] = self._parse_ccache_stats(result.stdout)
        except Exception:
            pass
        
        # Get SCCache stats
        try:
            result = subprocess.run(['sccache', '--show-stats'], capture_output=True, text=True)
            if result.returncode == 0:
                performance['sccache'] = self._parse_sccache_stats(result.stdout)
        except Exception:
            pass
        
        return performance
    
    def _parse_ccache_stats(self, stats_output: str) -> Dict:
        """Parse CCache statistics"""
        stats = {}
        for line in stats_output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                stats[key.strip()] = value.strip()
        return stats
    
    def _parse_sccache_stats(self, stats_output: str) -> Dict:
        """Parse SCCache statistics"""
        stats = {}
        for line in stats_output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                stats[key.strip()] = value.strip()
        return stats
    
    def run_optimization(self):
        """Run complete cache optimization"""
        print("🚀 Starting cache optimization...")
        
        try:
            # Generate cache keys
            cache_keys = self.optimize_cache_keys()
            
            # Set up compiler cache
            self.setup_compiler_cache()
            
            # Optimize parallelization
            self.optimize_build_parallelization()
            
            # Set up remote cache
            self.setup_remote_cache()
            
            # Clean up old cache
            self.cleanup_cache()
            
            # Generate report
            report = self.generate_cache_report()
            
            print("✅ Cache optimization completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Cache optimization failed: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Cache optimization for OpenSSL Conan packages')
    parser.add_argument('--config', default='conan-dev/cache-optimization.yml',
                       help='Path to cache optimization configuration file')
    parser.add_argument('--keys-only', action='store_true',
                       help='Only generate cache keys')
    parser.add_argument('--cleanup-only', action='store_true',
                       help='Only clean up cache')
    
    args = parser.parse_args()
    
    optimizer = CacheOptimizer(args.config)
    
    if args.keys_only:
        optimizer.optimize_cache_keys()
    elif args.cleanup_only:
        optimizer.cleanup_cache()
    else:
        success = optimizer.run_optimization()
        if not success:
            sys.exit(1)
    
    print("\n🎉 Cache optimization completed!")


if __name__ == '__main__':
    main()
