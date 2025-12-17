"""Tests for {{module_name}}."""

import pytest
from {{module_name}} import {{class_name}}, __version__


class Test{{class_name}}:
    """Test cases for {{class_name}}."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        instance = {{class_name}}()
        assert instance.config == {}
        assert instance.get_info()["name"] == "{{project_name}}"

    def test_init_with_config(self) -> None:
        """Test initialization with configuration."""
        config = {"key": "value", "number": 42}
        instance = {{class_name}}(config)
        assert instance.config == config

    def test_process_basic(self) -> None:
        """Test basic processing functionality."""
        instance = {{class_name}}()
        input_data = "test input"
        result = instance.process(input_data)

        assert isinstance(result, str)
        assert "{{project_name}}" in result
        assert input_data in result

    def test_process_empty_string(self) -> None:
        """Test processing empty string."""
        instance = {{class_name}}()
        result = instance.process("")

        assert isinstance(result, str)
        assert "{{project_name}}" in result

    def test_get_info(self) -> None:
        """Test get_info method."""
        config = {"test": True}
        instance = {{class_name}}(config)

        info = instance.get_info()

        assert info["name"] == "{{project_name}}"
        assert info["version"] == "{{version}}"
        assert info["description"] == "{{project_description}}"
        assert info["config"] == config


def test_version() -> None:
    """Test version is properly set."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0
    assert "{{version}}" == __version__