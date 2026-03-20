from unittest.mock import patch

import pytest

from utgen.test_generation_crew.llm_config import get_required_env


def test_get_required_env_returns_value():
    with patch("utgen.test_generation_crew.llm_config.os.getenv") as mock_getenv:
        mock_getenv.return_value = "secret_value"
        result = get_required_env("API_KEY")
        assert result == "secret_value"
        mock_getenv.assert_called_once_with("API_KEY")


def test_get_required_env_raises_value_error_when_unset():
    with patch("utgen.test_generation_crew.llm_config.os.getenv") as mock_getenv:
        mock_getenv.return_value = None
        with pytest.raises(ValueError, match="Missing required environment variable: API_KEY"):
            get_required_env("API_KEY")


def test_get_required_env_raises_value_error_when_empty():
    with patch("utgen.test_generation_crew.llm_config.os.getenv") as mock_getenv:
        mock_getenv.return_value = ""
        with pytest.raises(ValueError, match="Missing required environment variable: API_KEY"):
            get_required_env("API_KEY")
