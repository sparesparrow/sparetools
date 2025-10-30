#!/usr/bin/env python3
"""
Artifact Lifecycle Manager for OpenSSL Conan packages
Ensures proper cache invalidation and artifact lifecycle management
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
from datetime import datetime, timedelta


class ArtifactLifecycleManager:
    """Manages artifact lifecycle and cache invalidation"""
    
    def __init__(self, config_file: str = "conan-dev/artifact-lifecycle.yml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.artifact_registry = {}
        
    def _load_config(self) -> Dict:
        """Load artifact lifecycle configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default artifact lifecycle configuration"""
        return {
            'lifecycle': {
                'stages': ['development', 'testing', 'staging', 'production'],
                'retention_policies': {
                    'development': {'days': 7, 'versions': 3},
                    'testing': {'days': 14, 'versions': 5},
                    'staging': {'days': 30, 'versions': 10},
                    'production': {'days': 365, 'versions': 20}
                },
                'cache_invalidation': {
                    'source_changes': ['conanfile.py', 'VERSION.dat', 'configure', 'config'],
                    'binary_changes': ['settings.os', 'settings.arch', 'settings.compiler', 'options.fips'],
                    'dependency_changes': ['requirements.txt', 'conanfile.txt']
                }
            },
            'artifacts': {
                'package_types': ['source', 'binary', 'test', 'documentation'],
                'storage_backends': ['local', 'remote', 'archive'],
                'checksum_algorithms': ['sha256', 'sha512']
            }
        }
    
    def track_artifact(self, artifact_id: str, artifact_type: str, 
                      stage: str, metadata: Dict) -> bool:
        """Track artifact in lifecycle registry"""
        try:
            artifact_entry = {
                'id': artifact_id,
                'type': artifact_type,
                'stage': stage,
                'created_at': datetime.now().isoformat(),
                'metadata': metadata,
                'checksums': self._calculate_checksums(metadata.get('path', '')),
                'dependencies': metadata.get('dependencies', []),
                'cache_keys': metadata.get('cache_keys', {})
            }
            
            self.artifact_registry[artifact_id] = artifact_entry
            
            # Save to persistent storage
            self._save_artifact_registry()
            
            print(f"✓ Tracked artifact {artifact_id} in stage {stage}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to track artifact {artifact_id}: {e}")
            return False
    
    def _calculate_checksums(self, file_path: str) -> Dict[str, str]:
        """Calculate checksums for artifact"""
        checksums = {}
        
        if not os.path.exists(file_path):
            return checksums
        
        algorithms = self.config['artifacts']['checksum_algorithms']
        
        for algorithm in algorithms:
            try:
                hash_func = getattr(hashlib, algorithm)()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_func.update(chunk)
                checksums[algorithm] = hash_func.hexdigest()
            except Exception as e:
                print(f"Warning: Could not calculate {algorithm} for {file_path}: {e}")
        
        return checksums
    
    def invalidate_cache(self, change_type: str, changed_files: List[str]) -> List[str]:
        """Invalidate cache based on change type and files"""
        print(f"🔄 Invalidating cache for {change_type} changes...")
        
        invalidated_artifacts = []
        invalidation_rules = self.config['lifecycle']['cache_invalidation']
        
        # Determine what needs to be invalidated
        if change_type == 'source':
            affected_artifacts = self._find_artifacts_by_source_changes(changed_files)
        elif change_type == 'binary':
            affected_artifacts = self._find_artifacts_by_binary_changes(changed_files)
        elif change_type == 'dependency':
            affected_artifacts = self._find_artifacts_by_dependency_changes(changed_files)
        else:
            # Full invalidation
            affected_artifacts = list(self.artifact_registry.keys())
        
        # Invalidate affected artifacts
        for artifact_id in affected_artifacts:
            if self._invalidate_artifact(artifact_id):
                invalidated_artifacts.append(artifact_id)
        
        print(f"✓ Invalidated {len(invalidated_artifacts)} artifacts")
        return invalidated_artifacts
    
    def _find_artifacts_by_source_changes(self, changed_files: List[str]) -> List[str]:
        """Find artifacts affected by source changes"""
        affected = []
        source_patterns = self.config['lifecycle']['cache_invalidation']['source_changes']
        
        for artifact_id, artifact in self.artifact_registry.items():
            cache_keys = artifact.get('cache_keys', {})
            source_key = cache_keys.get('source', '')
            
            # Check if any changed file affects this artifact
            for changed_file in changed_files:
                if any(pattern in changed_file for pattern in source_patterns):
                    affected.append(artifact_id)
                    break
        
        return affected
    
    def _find_artifacts_by_binary_changes(self, changed_files: List[str]) -> List[str]:
        """Find artifacts affected by binary changes"""
        affected = []
        binary_patterns = self.config['lifecycle']['cache_invalidation']['binary_changes']
        
        for artifact_id, artifact in self.artifact_registry.items():
            cache_keys = artifact.get('cache_keys', {})
            binary_key = cache_keys.get('binary', '')
            
            # Check if any changed file affects this artifact
            for changed_file in changed_files:
                if any(pattern in changed_file for pattern in binary_patterns):
                    affected.append(artifact_id)
                    break
        
        return affected
    
    def _find_artifacts_by_dependency_changes(self, changed_files: List[str]) -> List[str]:
        """Find artifacts affected by dependency changes"""
        affected = []
        dep_patterns = self.config['lifecycle']['cache_invalidation']['dependency_changes']
        
        for artifact_id, artifact in self.artifact_registry.items():
            dependencies = artifact.get('dependencies', [])
            
            # Check if any changed file affects dependencies
            for changed_file in changed_files:
                if any(pattern in changed_file for pattern in dep_patterns):
                    affected.append(artifact_id)
                    break
        
        return affected
    
    def _invalidate_artifact(self, artifact_id: str) -> bool:
        """Invalidate a specific artifact"""
        try:
            if artifact_id not in self.artifact_registry:
                return False
            
            artifact = self.artifact_registry[artifact_id]
            
            # Mark as invalidated
            artifact['invalidated_at'] = datetime.now().isoformat()
            artifact['status'] = 'invalidated'
            
            # Remove from cache
            self._remove_artifact_from_cache(artifact)
            
            # Update registry
            self.artifact_registry[artifact_id] = artifact
            self._save_artifact_registry()
            
            print(f"  ✓ Invalidated artifact {artifact_id}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to invalidate artifact {artifact_id}: {e}")
            return False
    
    def _remove_artifact_from_cache(self, artifact: Dict):
        """Remove artifact from cache"""
        try:
            # Remove from Conan cache
            artifact_path = artifact.get('metadata', {}).get('path', '')
            if artifact_path and os.path.exists(artifact_path):
                subprocess.run(['conan', 'cache', 'clean', artifact_path], 
                             check=False, capture_output=True)
            
            # Remove from compiler cache if applicable
            if 'CCACHE_DIR' in os.environ:
                subprocess.run(['ccache', '-C'], check=False, capture_output=True)
            
        except Exception as e:
            print(f"Warning: Could not remove artifact from cache: {e}")
    
    def cleanup_old_artifacts(self) -> int:
        """Clean up old artifacts based on retention policies"""
        print("🧹 Cleaning up old artifacts...")
        
        cleaned_count = 0
        retention_policies = self.config['lifecycle']['retention_policies']
        
        for artifact_id, artifact in list(self.artifact_registry.items()):
            stage = artifact.get('stage', 'development')
            created_at = datetime.fromisoformat(artifact.get('created_at', ''))
            
            if stage in retention_policies:
                policy = retention_policies[stage]
                max_age = timedelta(days=policy['days'])
                
                if datetime.now() - created_at > max_age:
                    if self._cleanup_artifact(artifact_id, artifact):
                        cleaned_count += 1
        
        print(f"✓ Cleaned up {cleaned_count} old artifacts")
        return cleaned_count
    
    def _cleanup_artifact(self, artifact_id: str, artifact: Dict) -> bool:
        """Clean up a specific artifact"""
        try:
            # Remove from filesystem
            artifact_path = artifact.get('metadata', {}).get('path', '')
            if artifact_path and os.path.exists(artifact_path):
                if os.path.isfile(artifact_path):
                    os.remove(artifact_path)
                elif os.path.isdir(artifact_path):
                    import shutil
                    shutil.rmtree(artifact_path)
            
            # Remove from registry
            del self.artifact_registry[artifact_id]
            self._save_artifact_registry()
            
            print(f"  ✓ Cleaned up artifact {artifact_id}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to cleanup artifact {artifact_id}: {e}")
            return False
    
    def _save_artifact_registry(self):
        """Save artifact registry to persistent storage"""
        registry_file = 'artifact-registry.json'
        with open(registry_file, 'w') as f:
            json.dump(self.artifact_registry, f, indent=2)
    
    def generate_lifecycle_report(self) -> Dict:
        """Generate artifact lifecycle report"""
        print("📊 Generating lifecycle report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_artifacts': len(self.artifact_registry),
            'by_stage': {},
            'by_type': {},
            'retention_status': {},
            'cache_status': {}
        }
        
        # Analyze by stage
        for artifact in self.artifact_registry.values():
            stage = artifact.get('stage', 'unknown')
            artifact_type = artifact.get('type', 'unknown')
            
            if stage not in report['by_stage']:
                report['by_stage'][stage] = 0
            report['by_stage'][stage] += 1
            
            if artifact_type not in report['by_type']:
                report['by_type'][artifact_type] = 0
            report['by_type'][artifact_type] += 1
        
        # Check retention status
        retention_policies = self.config['lifecycle']['retention_policies']
        for stage, policy in retention_policies.items():
            max_age = timedelta(days=policy['days'])
            max_versions = policy['versions']
            
            stage_artifacts = [a for a in self.artifact_registry.values() 
                             if a.get('stage') == stage]
            
            old_artifacts = [a for a in stage_artifacts 
                           if datetime.now() - datetime.fromisoformat(a.get('created_at', '')) > max_age]
            
            report['retention_status'][stage] = {
                'total': len(stage_artifacts),
                'old': len(old_artifacts),
                'max_versions': max_versions,
                'needs_cleanup': len(stage_artifacts) > max_versions or len(old_artifacts) > 0
            }
        
        # Save report
        report_file = 'artifact-lifecycle-report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Lifecycle report saved: {report_file}")
        return report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Artifact Lifecycle Manager for OpenSSL Conan packages')
    parser.add_argument('--config', default='conan-dev/artifact-lifecycle.yml',
                       help='Path to artifact lifecycle configuration file')
    parser.add_argument('--track', nargs=3, metavar=('ID', 'TYPE', 'STAGE'),
                       help='Track a new artifact')
    parser.add_argument('--invalidate', nargs=2, metavar=('TYPE', 'FILES'),
                       help='Invalidate cache for changes')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up old artifacts')
    parser.add_argument('--report', action='store_true',
                       help='Generate lifecycle report')
    
    args = parser.parse_args()
    
    manager = ArtifactLifecycleManager(args.config)
    
    if args.track:
        artifact_id, artifact_type, stage = args.track
        metadata = {'path': f'artifacts/{artifact_id}', 'cache_keys': {}}
        success = manager.track_artifact(artifact_id, artifact_type, stage, metadata)
    elif args.invalidate:
        change_type, files_str = args.invalidate
        changed_files = files_str.split(',')
        invalidated = manager.invalidate_cache(change_type, changed_files)
        success = len(invalidated) > 0
    elif args.cleanup:
        cleaned = manager.cleanup_old_artifacts()
        success = cleaned >= 0
    elif args.report:
        report = manager.generate_lifecycle_report()
        success = True
    else:
        print("Please specify an action: --track, --invalidate, --cleanup, or --report")
        success = False
    
    if not success:
        sys.exit(1)
    else:
        print("\n🎉 Artifact lifecycle management completed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
