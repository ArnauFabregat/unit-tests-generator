import logging

from utgen.logger import disable_dependency_loggers


def test_disable_dependency_loggers_with_valid_dependencies():
    """
    Test disable_dependency_loggers with a list of valid library names.
    """
    # Arrange
    dependencies = ["requests", "numpy", "pandas"]

    # Act
    disable_dependency_loggers(dependencies)

    # Assert
    for name in dependencies:
        logger = logging.getLogger(name)
        assert logger.disabled is True
        assert logger.propagate is False


def test_disable_dependency_loggers_with_empty_list():
    """
    Test disable_dependency_loggers with an empty list.
    """
    # Arrange
    dependencies = []

    # Act
    disable_dependency_loggers(dependencies)

    # Assert
    # No exceptions should be raised
    pass


def test_disable_dependency_loggers_with_invalid_names():
    """
    Test disable_dependency_loggers with invalid library names.
    """
    # Arrange
    dependencies = ["nonexistent_library_123", "another_invalid_456"]

    # Act
    disable_dependency_loggers(dependencies)

    # Assert
    # No exceptions should be raised even for invalid names
    for name in dependencies:
        logger = logging.getLogger(name)
        assert logger.disabled is True
        assert logger.propagate is False


def test_disable_dependency_loggers_with_mixed_valid_and_invalid():
    """
    Test disable_dependency_loggers with a mix of valid and invalid library names.
    """
    # Arrange
    dependencies = ["requests", "invalid_lib_123", "numpy", "another_invalid_456"]

    # Act
    disable_dependency_loggers(dependencies)

    # Assert
    for name in dependencies:
        logger = logging.getLogger(name)
        assert logger.disabled is True
        assert logger.propagate is False
