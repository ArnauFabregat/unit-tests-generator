import logging
from unittest.mock import Mock

from utgen.logger import disable_dependency_loggers


def test_disable_dependency_loggers_basic():
    # Mock the logging.getLogger method
    mock_get_logger = Mock()
    logging.getLogger = mock_get_logger

    # Test with a basic list of dependencies
    dependencies = ["dependency1", "dependency2"]

    # Call the function
    disable_dependency_loggers(dependencies)

    # Verify that getLogger was called for each dependency
    mock_get_logger.assert_any_call("dependency1")
    mock_get_logger.assert_any_call("dependency2")

    # Verify that disabled and propagate were set to True and False respectively
    mock_get_logger.return_value.disabled = True
    mock_get_logger.return_value.propagate = False


def test_disable_dependency_loggers_empty_list():
    # Mock the logging.getLogger method
    mock_get_logger = Mock()
    logging.getLogger = mock_get_logger

    # Test with an empty list
    dependencies = []

    # Call the function
    disable_dependency_loggers(dependencies)

    # Verify that getLogger was never called
    mock_get_logger.assert_not_called()
