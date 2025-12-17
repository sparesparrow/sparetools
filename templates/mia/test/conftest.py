"""Pytest configuration and fixtures."""

import pytest
import logging
from typing import Generator


@pytest.fixture(autouse=True)
def setup_logging(caplog: pytest.LogCaptureFixture) -> Generator[None, None, None]:
    """Set up logging for tests."""
    caplog.set_level(logging.DEBUG)


@pytest.fixture
def sample_config() -> dict[str, str]:
    """Sample configuration for testing."""
    return {
        "api_url": "https://api.example.com",
        "timeout": "30",
        "debug": "true",
    }