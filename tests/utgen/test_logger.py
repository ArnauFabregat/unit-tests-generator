import logging

from loguru import logger

from utgen.logger import disable_dependency_loggers, setup_logger


def test_disable_dependency_loggers_with_valid_dependencies():
    """
    Test disable_dependency_loggers with a list of valid dependency names.
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
    # No exceptions should be raised, and no loggers should be modified
    pass


def test_disable_dependency_loggers_with_nonexistent_dependencies():
    """
    Test disable_dependency_loggers with names that don't correspond to actual loggers.
    """
    # Arrange
    dependencies = ["nonexistent_library_1", "nonexistent_library_2"]

    # Act
    disable_dependency_loggers(dependencies)

    # Assert
    for name in dependencies:
        logger = logging.getLogger(name)
        assert logger.disabled is True
        assert logger.propagate is False


def test_disable_dependency_loggers_with_mixed_case_names():
    """
    Test disable_dependency_loggers with mixed case dependency names.
    """
    # Arrange
    dependencies = ["ReQuEsTs", "NumPy", "PANDAS"]

    # Act
    disable_dependency_loggers(dependencies)

    # Assert
    for name in dependencies:
        logger = logging.getLogger(name)
        assert logger.disabled is True
        assert logger.propagate is False


def test_setup_logger_removes_default_handler():
    """
    Test that setup_logger removes the default Loguru handler.
    """
    # Act
    setup_logger()

    # Assert
    # Verify that the number of handlers is 2 (stdout and stderr)
    final_handlers = logger._core.handlers
    assert len(final_handlers) == 2

    # Verify that the default handler was removed
    # (We can't directly check for the default handler, but we know it should be gone)
