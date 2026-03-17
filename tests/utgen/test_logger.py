from unittest.mock import patch

from utgen.logger import disable_dependency_loggers


def test_disable_dependency_loggers_with_valid_dependencies():
    """
    Test disable_dependency_loggers with a valid list of dependencies.
    """
    # Arrange
    dependencies = ["requests", "numpy", "pandas"]

    with patch("logging.getLogger") as mock_get_logger:
        # Act
        disable_dependency_loggers(dependencies)

        # Assert
        assert mock_get_logger.call_count == 6
        for name in dependencies:
            mock_get_logger.assert_any_call(name)
            mock_get_logger(name).disabled = True
            mock_get_logger(name).propagate = False


def test_disable_dependency_loggers_with_empty_list():
    """
    Test disable_dependency_loggers with an empty list.
    """
    # Arrange
    dependencies = []

    with patch("logging.getLogger") as mock_get_logger:
        # Act
        disable_dependency_loggers(dependencies)

        # Assert
        mock_get_logger.assert_not_called()


def test_disable_dependency_loggers_with_duplicate_names():
    """
    Test disable_dependency_loggers with duplicate library names.
    """
    # Arrange
    dependencies = ["requests", "requests", "numpy"]

    with patch("logging.getLogger") as mock_get_logger:
        # Act
        disable_dependency_loggers(dependencies)

        # Assert
        assert mock_get_logger.call_count == 6
        for name in ["requests", "numpy"]:
            mock_get_logger.assert_any_call(name)
            mock_get_logger(name).disabled = True
            mock_get_logger(name).propagate = False
