"""Pytest configuration and fixtures for SpareTools tests"""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def tmp_path(request):
    """Enhanced tmp_path fixture that cleans up after tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
