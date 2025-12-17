"""Tests for mia_project."""

import pytest
from mia_project import MiaProject, __version__


class TestMiaProject:
    """Test cases for MiaProject."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        instance = MiaProject()
        assert instance.config == {}
        assert instance.get_info()["name"] == "mia-project"

    def test_init_with_config(self) -> None:
        """Test initialization with configuration."""
        config = {"key": "value", "number": 42}
        instance = MiaProject(config)
        assert instance.config == config

    def test_process_basic(self) -> None:
        """Test basic processing functionality."""
        instance = MiaProject()
        input_data = "test input"
        result = instance.process(input_data)

        assert isinstance(result, str)
        assert "mia-project" in result
        assert input_data in result

    def test_process_empty_string(self) -> None:
        """Test processing empty string."""
        instance = MiaProject()
        result = instance.process("")

        assert isinstance(result, str)
        assert "mia-project" in result

    def test_get_info(self) -> None:
        """Test get_info method."""
        config = {"test": True}
        instance = MiaProject(config)

        info = instance.get_info()

        assert info["name"] == "mia-project"
        assert info["version"] == "1.0.0"
        assert info["description"] == "{{project_description}}"
        assert info["config"] == config


def test_version() -> None:
    """Test version is properly set."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0
    assert "1.0.0" == __version__