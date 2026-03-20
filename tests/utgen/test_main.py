import json
from unittest.mock import Mock, patch

import pytest

from utgen.main import run


def test_run_normal_execution(tmp_path):
    """Test run function with normal execution."""
    # Arrange
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    with (
        patch("utgen.main.pipeline") as mock_pipeline,
        patch("utgen.main.LLM") as mock_llm_class,
        patch("utgen.main.subprocess.run") as mock_subprocess,
    ):
        # Mock LLM instance
        mock_llm_instance = Mock()
        mock_llm_class.return_value = mock_llm_instance

        # Act
        run(src_path=src_dir, test_path=test_dir, overwrite=False, model="test-model", temperature=0.5, max_tokens=1000)

        # Assert
        # Verify pipeline was called with correct arguments
        mock_pipeline.assert_called_once()
        args, kwargs = mock_pipeline.call_args
        assert kwargs["source_code_dir"] == str(src_dir)
        assert kwargs["tests_output_dir"] == str(test_dir)
        assert kwargs["save_graph_path"] == ""
        assert kwargs["overwrite"] is False
        assert kwargs["llm"] == mock_llm_instance

        # Verify subprocess.run was called for coverage
        mock_subprocess.assert_called_once()
        args, kwargs = mock_subprocess.call_args
        assert args[0] == ["pytest", str(test_dir), f"--cov={src_dir}", "--cov-report=term-missing"]
        assert kwargs["check"] is True


def test_run_invalid_llm_extra(tmp_path):
    """Test run function raises JSONDecodeError for invalid llm_extra."""
    # Arrange
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    # Act & Assert
    with pytest.raises(json.JSONDecodeError):
        run(src_path=src_dir, test_path=test_dir, llm_extra="{invalid json}")
