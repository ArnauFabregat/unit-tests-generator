from unittest.mock import patch

import pytest

from utgen.logger import disable_dependency_loggers


def test_disable_dependency_loggers_with_empty_list():
    """
    Test disable_dependency_loggers with an empty list.
    """
    # Arrange
    dependencies = []

    # Use patch to mock the logging.getLogger calls
    with patch("logging.getLogger") as mock_get_logger:
        # Act
        disable_dependency_loggers(dependencies)

        # Assert
        # Verify that getLogger was never called
        mock_get_logger.assert_not_called()


def test_disable_dependency_loggers_with_none_input():
    """
    Test disable_dependency_loggers with None input (should raise TypeError).
    """
    # Arrange
    dependencies = None

    # Use patch to mock the logging.getLogger calls
    with patch("logging.getLogger") as mock_get_logger:
        # Act and Assert
        with pytest.raises(TypeError):
            disable_dependency_loggers(dependencies)
