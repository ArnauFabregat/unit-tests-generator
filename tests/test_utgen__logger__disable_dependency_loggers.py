from unittest.mock import patch

from utgen.logger import disable_dependency_loggers


@patch("logging.getLogger")
def test_disable_dependency_loggers_empty_list(mock_getLogger):
    # Arrange
    dependencies = []

    # Act
    disable_dependency_loggers(dependencies)

    # Assert
    mock_getLogger.assert_not_called()
