"""Unit tests for sparetools-base symlink-helpers module"""
import os
import tempfile
import pytest
from pathlib import Path

# Import the module we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "sparetools-base"))

from symlink_helpers import (
    symlink_with_check,
    symlink_all_child_folders,
    validate_zero_copy_setup,
    get_conan_cache_stats
)


class TestSymlinkWithCheck:
    """Tests for symlink_with_check function"""
    
    def test_symlink_creates_when_destination_missing(self, tmp_path):
        """Test symlink creation when destination doesn't exist"""
        source = tmp_path / "source"
        source.mkdir()
        (source / "file.txt").write_text("test")
        
        destination = tmp_path / "link"
        
        result = symlink_with_check(str(source), str(destination), target_is_directory=True)
        
        assert result is True
        assert os.path.islink(str(destination))
        assert os.path.exists(str(destination))
        assert os.readlink(str(destination)) == str(source)
    
    def test_symlink_skips_when_destination_exists(self, tmp_path):
        """Test symlink skips when destination already exists"""
        source = tmp_path / "source"
        source.mkdir()
        
        destination = tmp_path / "link"
        destination.mkdir()  # Create existing directory
        
        result = symlink_with_check(str(source), str(destination), target_is_directory=True)
        
        assert result is False
        assert not os.path.islink(str(destination))
    
    def test_symlink_raises_when_source_missing(self, tmp_path):
        """Test symlink raises FileNotFoundError when source doesn't exist"""
        source = tmp_path / "nonexistent"
        destination = tmp_path / "link"
        
        with pytest.raises(FileNotFoundError):
            symlink_with_check(str(source), str(destination), target_is_directory=True)


class TestSymlinkAllChildFolders:
    """Tests for symlink_all_child_folders function"""
    
    def test_symlinks_all_subdirectories(self, tmp_path):
        """Test that all subdirectories are symlinked"""
        source_root = tmp_path / "source"
        source_root.mkdir()
        
        (source_root / "dir1").mkdir()
        (source_root / "dir2").mkdir()
        (source_root / "file.txt").write_text("ignore me")
        
        dest_root = tmp_path / "dest"
        
        stats = symlink_all_child_folders(str(source_root), str(dest_root))
        
        assert stats["created"] == 2
        assert stats["skipped"] == 0
        assert stats["failed"] == 0
        assert len(stats["paths"]) == 2
        
        assert os.path.islink(str(dest_root / "dir1"))
        assert os.path.islink(str(dest_root / "dir2"))
        assert not os.path.exists(str(dest_root / "file.txt"))  # Files not symlinked
    
    def test_handles_empty_source(self, tmp_path):
        """Test handling of empty source directory"""
        source_root = tmp_path / "source"
        source_root.mkdir()
        
        dest_root = tmp_path / "dest"
        
        stats = symlink_all_child_folders(str(source_root), str(dest_root))
        
        assert stats["created"] == 0
        assert stats["skipped"] == 0
        assert stats["failed"] == 0
    
    def test_raises_when_source_missing(self, tmp_path):
        """Test raises FileNotFoundError when source root doesn't exist"""
        source_root = tmp_path / "nonexistent"
        dest_root = tmp_path / "dest"
        
        with pytest.raises(FileNotFoundError):
            symlink_all_child_folders(str(source_root), str(dest_root))


class TestValidateZeroCopySetup:
    """Tests for validate_zero_copy_setup function"""
    
    def test_detects_symlinks(self, tmp_path):
        """Test that symlinks are detected correctly"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        # Create a symlink
        real_dir = tmp_path / "real"
        real_dir.mkdir()
        (workspace / "link").symlink_to(real_dir)
        
        results = validate_zero_copy_setup(str(workspace))
        
        assert results["total_symlinks"] >= 1
        assert results["total_copies"] == 0
    
    def test_validates_expected_symlinks(self, tmp_path):
        """Test validation of expected symlink paths"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        real_dir = tmp_path / "real"
        real_dir.mkdir()
        (workspace / "python").symlink_to(real_dir)
        
        results = validate_zero_copy_setup(
            str(workspace),
            expected_symlinks=["python"]
        )
        
        assert "python" in results["expected_found"]
        assert len(results["expected_missing"]) == 0
    
    def test_detects_missing_expected_symlinks(self, tmp_path):
        """Test detection of missing expected symlinks"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        results = validate_zero_copy_setup(
            str(workspace),
            expected_symlinks=["python", "openssl"]
        )
        
        assert len(results["expected_missing"]) == 2
        assert "python" in results["expected_missing"]
        assert "openssl" in results["expected_missing"]


class TestGetConanCacheStats:
    """Tests for get_conan_cache_stats function"""
    
    def test_handles_missing_cache(self, monkeypatch):
        """Test handling when Conan cache doesn't exist"""
        # Mock home directory to point to non-existent cache
        fake_home = tempfile.mkdtemp()
        monkeypatch.setenv("HOME", fake_home)
        
        stats = get_conan_cache_stats()
        
        assert stats["total_packages"] == 0
        assert stats["total_size_mb"] == 0
        assert stats["packages"] == []
