#!/usr/bin/env python3
"""
OpenSSL Tools - Build Cache Manager
Manages build cache and optimization for faster builds.
"""

import hashlib
import json
import os
import shutil
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import pickle
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BuildInfo:
    """Information about a build configuration."""
    source_files: List[str]
    build_options: Dict[str, Any]
    dependencies: List[str]
    compiler: str
    compiler_version: str
    target_arch: str
    build_type: str
    timestamp: datetime
    build_hash: str
    artifacts_path: str
    build_time: float
    success: bool


class BuildCacheManager:
    """Manages build cache and optimization."""
    
    def __init__(self, cache_dir: Path = None, max_cache_size_gb: int = 10, retention_days: int = 30):
        self.cache_dir = cache_dir or Path.home() / ".openssl-build-cache"
        self.max_cache_size_gb = max_cache_size_gb
        self.retention_days = retention_days  # Cache retention policy in days
        self.index_file = self.cache_dir / "build_index.json"
        self.stats_file = self.cache_dir / "cache_stats.json"
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing index
        self.build_index = self._load_index()
        self.cache_stats = self._load_stats()
        
        # Apply retention policy on initialization
        self._apply_retention_policy()
        
    def calculate_build_hash(self, source_files: List[Path], 
                           build_options: Dict[str, Any],
                           dependencies: List[str] = None,
                           compiler_info: Dict[str, str] = None) -> str:
        """
        Calculate hash for build configuration.
        
        Args:
            source_files: List of source file paths
            build_options: Build configuration options
            dependencies: List of dependency names/versions
            compiler_info: Compiler information
            
        Returns:
            str: SHA256 hash of the build configuration
        """
        hasher = hashlib.sha256()
        
        # Hash source files
        for file_path in sorted(source_files):
            if file_path.exists():
                # Include file content and modification time
                stat = file_path.stat()
                hasher.update(f"{file_path}:{stat.st_mtime}:{stat.st_size}".encode())
                hasher.update(file_path.read_bytes())
            else:
                logger.warning(f"Source file not found: {file_path}")
                
        # Hash build options (sorted for consistency)
        hasher.update(json.dumps(build_options, sort_keys=True).encode())
        
        # Hash dependencies
        if dependencies:
            hasher.update(json.dumps(sorted(dependencies), sort_keys=True).encode())
            
        # Hash compiler info
        if compiler_info:
            hasher.update(json.dumps(compiler_info, sort_keys=True).encode())
            
        return hasher.hexdigest()
        
    def get_cached_artifacts(self, build_hash: str) -> Optional[Path]:
        """
        Get cached build artifacts if available.
        
        Args:
            build_hash: Build configuration hash
            
        Returns:
            Path to cached artifacts or None if not found
        """
        if build_hash in self.build_index:
            cache_path = self.cache_dir / build_hash
            if cache_path.exists():
                # Update access time
                self.build_index[build_hash]["last_accessed"] = datetime.now().isoformat()
                self._save_index()
                
                # Update cache stats
                self.cache_stats["cache_hits"] += 1
                self._save_stats()
                
                logger.info(f"Cache hit for build hash: {build_hash[:8]}...")
                return cache_path
                
        # Cache miss
        self.cache_stats["cache_misses"] += 1
        self._save_stats()
        
        logger.info(f"Cache miss for build hash: {build_hash[:8]}...")
        return None
        
    def store_artifacts(self, build_hash: str, artifacts_path: Path,
                       build_info: BuildInfo) -> bool:
        """
        Store build artifacts in cache.
        
        Args:
            build_hash: Build configuration hash
            artifacts_path: Path to build artifacts
            build_info: Build information
            
        Returns:
            bool: True if storage was successful
        """
        try:
            cache_path = self.cache_dir / build_hash
            
            # Remove existing cache entry if it exists
            if cache_path.exists():
                shutil.rmtree(cache_path)
                
            # Copy artifacts to cache
            shutil.copytree(artifacts_path, cache_path)
            
            # Store build info
            build_info.artifacts_path = str(cache_path)
            self.build_index[build_hash] = {
                "build_info": asdict(build_info),
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "size_bytes": self._get_directory_size(cache_path)
            }
            
            self._save_index()
            
            # Update cache stats
            self.cache_stats["total_builds"] += 1
            self.cache_stats["cache_size_bytes"] = self._get_cache_size()
            self._save_stats()
            
            logger.info(f"Stored artifacts in cache: {build_hash[:8]}...")
            
            # Check if cache cleanup is needed
            self._cleanup_cache_if_needed()
            
            # Apply retention policy after storing new artifacts
            self._apply_retention_policy()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store artifacts: {e}")
            return False
            
    def _get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes."""
        total_size = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
        
    def _get_cache_size(self) -> int:
        """Get total cache size in bytes."""
        return self._get_directory_size(self.cache_dir)
        
    def _cleanup_cache_if_needed(self):
        """Clean up cache if it exceeds maximum size."""
        cache_size_gb = self._get_cache_size() / (1024**3)
        
        if cache_size_gb > self.max_cache_size_gb:
            logger.info(f"Cache size ({cache_size_gb:.2f} GB) exceeds limit ({self.max_cache_size_gb} GB)")
            self._cleanup_cache()
            
    def _cleanup_cache(self):
        """Clean up cache by removing oldest entries."""
        # Sort by last accessed time
        sorted_entries = sorted(
            self.build_index.items(),
            key=lambda x: x[1].get("last_accessed", "1970-01-01")
        )
        
        # Remove oldest entries until we're under the limit
        target_size_gb = self.max_cache_size_gb * 0.8  # Clean to 80% of limit
        
        for build_hash, entry in sorted_entries:
            cache_size_gb = self._get_cache_size() / (1024**3)
            if cache_size_gb <= target_size_gb:
                break
                
            cache_path = self.cache_dir / build_hash
            if cache_path.exists():
                shutil.rmtree(cache_path)
                del self.build_index[build_hash]
                logger.info(f"Removed cache entry: {build_hash[:8]}...")
                
        self._save_index()
        
    def _apply_retention_policy(self):
        """Apply retention policy to remove old cache entries."""
        if self.retention_days <= 0:
            return
            
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        removed_count = 0
        
        for build_hash, entry in list(self.build_index.items()):
            try:
                created_at = datetime.fromisoformat(entry.get("created_at", "1970-01-01"))
                if created_at < cutoff_date:
                    cache_path = self.cache_dir / build_hash
                    if cache_path.exists():
                        shutil.rmtree(cache_path)
                    del self.build_index[build_hash]
                    removed_count += 1
                    logger.info(f"Removed expired cache entry: {build_hash[:8]}... (created: {created_at.date()})")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid date format in cache entry {build_hash[:8]}: {e}")
                # Remove malformed entries
                cache_path = self.cache_dir / build_hash
                if cache_path.exists():
                    shutil.rmtree(cache_path)
                del self.build_index[build_hash]
                removed_count += 1
                
        if removed_count > 0:
            self._save_index()
            logger.info(f"Retention policy applied: removed {removed_count} expired cache entries (older than {self.retention_days} days)")
            
    def get_retention_stats(self) -> Dict:
        """Get retention policy statistics."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        total_entries = len(self.build_index)
        expired_entries = 0
        total_size_bytes = 0
        expired_size_bytes = 0
        
        for build_hash, entry in self.build_index.items():
            try:
                created_at = datetime.fromisoformat(entry.get("created_at", "1970-01-01"))
                size_bytes = entry.get("size_bytes", 0)
                total_size_bytes += size_bytes
                
                if created_at < cutoff_date:
                    expired_entries += 1
                    expired_size_bytes += size_bytes
            except (ValueError, TypeError):
                # Count malformed entries as expired
                expired_entries += 1
                expired_size_bytes += entry.get("size_bytes", 0)
                
        return {
            "retention_days": self.retention_days,
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "total_size_gb": total_size_bytes / (1024**3),
            "expired_size_gb": expired_size_bytes / (1024**3),
            "active_size_gb": (total_size_bytes - expired_size_bytes) / (1024**3),
            "cutoff_date": cutoff_date.isoformat()
        }
        
    def list_cached_builds(self) -> List[Dict]:
        """List all cached builds."""
        builds = []
        for build_hash, entry in self.build_index.items():
            build_info = entry.get("build_info", {})
            builds.append({
                "hash": build_hash,
                "created_at": entry.get("created_at"),
                "last_accessed": entry.get("last_accessed"),
                "size_bytes": entry.get("size_bytes", 0),
                "build_time": build_info.get("build_time", 0),
                "success": build_info.get("success", False)
            })
            
        return sorted(builds, key=lambda x: x["last_accessed"], reverse=True)
        
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        cache_size_gb = self._get_cache_size() / (1024**3)
        hit_rate = 0
        
        total_requests = self.cache_stats.get("cache_hits", 0) + self.cache_stats.get("cache_misses", 0)
        if total_requests > 0:
            hit_rate = self.cache_stats.get("cache_hits", 0) / total_requests
            
        # Get retention statistics
        retention_stats = self.get_retention_stats()
            
        return {
            "cache_size_gb": cache_size_gb,
            "max_cache_size_gb": self.max_cache_size_gb,
            "cache_hits": self.cache_stats.get("cache_hits", 0),
            "cache_misses": self.cache_stats.get("cache_misses", 0),
            "hit_rate": hit_rate,
            "total_builds": self.cache_stats.get("total_builds", 0),
            "cached_builds": len(self.build_index),
            "retention_policy": {
                "retention_days": self.retention_days,
                "active_entries": retention_stats["active_entries"],
                "expired_entries": retention_stats["expired_entries"],
                "active_size_gb": retention_stats["active_size_gb"],
                "expired_size_gb": retention_stats["expired_size_gb"]
            }
        }
        
    def clear_cache(self, older_than_days: int = None) -> int:
        """
        Clear cache entries.
        
        Args:
            older_than_days: Only clear entries older than this many days
            
        Returns:
            int: Number of entries cleared
        """
        cleared_count = 0
        cutoff_date = None
        
        if older_than_days:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            
        for build_hash, entry in list(self.build_index.items()):
            should_clear = False
            
            if cutoff_date:
                created_at = datetime.fromisoformat(entry.get("created_at", "1970-01-01"))
                should_clear = created_at < cutoff_date
            else:
                should_clear = True
                
            if should_clear:
                cache_path = self.cache_dir / build_hash
                if cache_path.exists():
                    shutil.rmtree(cache_path)
                del self.build_index[build_hash]
                cleared_count += 1
                
        if cleared_count > 0:
            self._save_index()
            logger.info(f"Cleared {cleared_count} cache entries")
            
        return cleared_count
        
    def _load_index(self) -> Dict:
        """Load build index from file."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load build index: {e}")
        return {}
        
    def _save_index(self):
        """Save build index to file."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.build_index, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save build index: {e}")
            
    def _load_stats(self) -> Dict:
        """Load cache statistics from file."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache stats: {e}")
        return {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_builds": 0,
            "cache_size_bytes": 0
        }
        
    def _save_stats(self):
        """Save cache statistics to file."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.cache_stats, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save cache stats: {e}")


class BuildOptimizer:
    """Build optimization utilities."""
    
    def __init__(self, cache_manager: BuildCacheManager = None):
        self.cache_manager = cache_manager or BuildCacheManager()
        
    def optimize_build_command(self, base_command: List[str],
                             source_files: List[Path],
                             build_options: Dict[str, Any]) -> List[str]:
        """
        Optimize build command based on cache and best practices.
        
        Args:
            base_command: Base build command
            source_files: List of source files
            build_options: Build options
            
        Returns:
            Optimized build command
        """
        optimized_command = base_command.copy()
        
        # Add parallel build options if supported
        if any("make" in cmd for cmd in base_command):
            # Add parallel make option
            optimized_command.extend(["-j", str(os.cpu_count())])
            
        # Add optimization flags
        if build_options.get("build_type") == "Release":
            optimized_command.extend(["-O3", "-DNDEBUG"])
            
        # Add cache directory if using ccache
        if shutil.which("ccache"):
            optimized_command.insert(0, "ccache")
            
        return optimized_command
        
    def should_use_cache(self, build_hash: str, 
                        force_rebuild: bool = False) -> bool:
        """
        Determine if cache should be used for this build.
        
        Args:
            build_hash: Build configuration hash
            force_rebuild: Force rebuild even if cache exists
            
        Returns:
            bool: True if cache should be used
        """
        if force_rebuild:
            return False
            
        cached_artifacts = self.cache_manager.get_cached_artifacts(build_hash)
        return cached_artifacts is not None
        
    def get_build_dependencies(self, source_files: List[Path]) -> List[str]:
        """
        Extract build dependencies from source files.
        
        Args:
            source_files: List of source files
            
        Returns:
            List of dependency names
        """
        dependencies = set()
        
        for file_path in source_files:
            if file_path.suffix in ['.c', '.cpp', '.cc', '.cxx']:
                # Parse includes to find dependencies
                try:
                    content = file_path.read_text()
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('#include'):
                            # Extract include path
                            include = line.split('"')[1] if '"' in line else line.split('<')[1].split('>')[0]
                            if '/' in include:
                                dependencies.add(include.split('/')[0])
                except (IOError, UnicodeDecodeError):
                    continue
                    
        return list(dependencies)


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Build Cache Manager")
    parser.add_argument("--cache-dir", type=Path, help="Cache directory path")
    parser.add_argument("--max-size", type=int, default=10, help="Max cache size in GB")
    parser.add_argument("--retention-days", type=int, default=30, help="Cache retention policy in days (default: 30)")
    parser.add_argument("--list", action="store_true", help="List cached builds")
    parser.add_argument("--stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--retention-stats", action="store_true", help="Show retention policy statistics")
    parser.add_argument("--apply-retention", action="store_true", help="Apply retention policy manually")
    parser.add_argument("--clear", type=int, help="Clear cache entries older than N days")
    parser.add_argument("--clear-all", action="store_true", help="Clear all cache entries")
    
    args = parser.parse_args()
    
    cache_manager = BuildCacheManager(
        cache_dir=args.cache_dir,
        max_cache_size_gb=args.max_size,
        retention_days=args.retention_days
    )
    
    if args.list:
        builds = cache_manager.list_cached_builds()
        if builds:
            print("Cached builds:")
            for build in builds:
                size_mb = build["size_bytes"] / (1024**2)
                print(f"  {build['hash'][:8]}... - {size_mb:.1f} MB - {build['last_accessed']}")
        else:
            print("No cached builds found")
            
    if args.stats:
        stats = cache_manager.get_cache_stats()
        print("Cache Statistics:")
        print(f"  Size: {stats['cache_size_gb']:.2f} GB / {stats['max_cache_size_gb']} GB")
        print(f"  Hit Rate: {stats['hit_rate']:.1%}")
        print(f"  Cache Hits: {stats['cache_hits']}")
        print(f"  Cache Misses: {stats['cache_misses']}")
        print(f"  Total Builds: {stats['total_builds']}")
        print(f"  Cached Builds: {stats['cached_builds']}")
        print(f"  Retention Policy: {stats['retention_policy']['retention_days']} days")
        print(f"  Active Entries: {stats['retention_policy']['active_entries']}")
        print(f"  Expired Entries: {stats['retention_policy']['expired_entries']}")
        
    if args.retention_stats:
        retention_stats = cache_manager.get_retention_stats()
        print("Retention Policy Statistics:")
        print(f"  Retention Period: {retention_stats['retention_days']} days")
        print(f"  Cutoff Date: {retention_stats['cutoff_date']}")
        print(f"  Total Entries: {retention_stats['total_entries']}")
        print(f"  Active Entries: {retention_stats['active_entries']}")
        print(f"  Expired Entries: {retention_stats['expired_entries']}")
        print(f"  Total Size: {retention_stats['total_size_gb']:.2f} GB")
        print(f"  Active Size: {retention_stats['active_size_gb']:.2f} GB")
        print(f"  Expired Size: {retention_stats['expired_size_gb']:.2f} GB")
        
    if args.apply_retention:
        print(f"Applying retention policy ({args.retention_days} days)...")
        cache_manager._apply_retention_policy()
        print("Retention policy applied successfully")
        
    if args.clear:
        cleared = cache_manager.clear_cache(older_than_days=args.clear)
        print(f"Cleared {cleared} cache entries older than {args.clear} days")
        
    if args.clear_all:
        cleared = cache_manager.clear_cache()
        print(f"Cleared {cleared} cache entries")


if __name__ == "__main__":
    main()