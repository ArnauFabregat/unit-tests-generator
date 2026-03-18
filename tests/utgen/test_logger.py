import logging
import sys
from unittest.mock import patch

from loguru import logger

from utgen.logger import LOG_FORMAT, disable_dependency_loggers, setup_logger


def test_disable_dependency_loggers_with_multiple_dependencies():
    """Test that disable_dependency_loggers disables multiple loggers."""
    dependencies = ["test_lib1", "test_lib2"]
    disable_dependency_loggers(dependencies)
    for name in dependencies:
        logger = logging.getLogger(name)
        assert logger.disabled is True
        assert logger.propagate is False


def test_disable_dependency_loggers_with_empty_list():
    """Test that disable_dependency_loggers handles empty list without error."""
    disable_dependency_loggers([])
    # No exception is raised


def test_disable_dependency_loggers_with_single_dependency():
    """Test that disable_dependency_loggers disables a single dependency."""
    dependency = "test_lib_single"
    disable_dependency_loggers([dependency])
    logger = logging.getLogger(dependency)
    assert logger.disabled is True
    assert logger.propagate is False


def test_disable_dependency_loggers_with_duplicates():
    """Test that disable_dependency_loggers handles duplicate dependencies correctly."""
    dependencies = ["test_lib_dup", "test_lib_dup"]
    disable_dependency_loggers(dependencies)
    logger = logging.getLogger("test_lib_dup")
    assert logger.disabled is True
    assert logger.propagate is False


def test_setup_logger_debug_true():
    """Test setup_logger with debug=True sets DEBUG level for stdout."""
    with patch.object(logger, "remove") as mock_remove, patch.object(logger, "add") as mock_add:
        setup_logger(debug=True)

        mock_remove.assert_called_once()

        calls = mock_add.call_args_list
        assert len(calls) == 2

        # First call: stdout handler with DEBUG level
        stdout_call = calls[0]
        assert stdout_call[0][0] == sys.stdout
        assert stdout_call[1]["level"] == "DEBUG"
        assert stdout_call[1]["format"] == LOG_FORMAT
        assert callable(stdout_call[1]["filter"])

        # Second call: stderr handler with WARNING level
        stderr_call = calls[1]
        assert stderr_call[0][0] == sys.stderr
        assert stderr_call[1]["level"] == "WARNING"
        assert stderr_call[1]["format"] == "\n" + LOG_FORMAT


def test_setup_logger_debug_false():
    """Test setup_logger with debug=False sets INFO level for stdout."""
    with patch.object(logger, "remove") as mock_remove, patch.object(logger, "add") as mock_add:
        setup_logger(debug=False)

        mock_remove.assert_called_once()

        calls = mock_add.call_args_list
        assert len(calls) == 2

        # First call: stdout handler with INFO level
        stdout_call = calls[0]
        assert stdout_call[0][0] == sys.stdout
        assert stdout_call[1]["level"] == "INFO"
        assert stdout_call[1]["format"] == LOG_FORMAT

        # Second call: stderr handler with WARNING level
        stderr_call = calls[1]
        assert stderr_call[0][0] == sys.stderr
        assert stderr_call[1]["level"] == "WARNING"


def test_setup_logger_debug_none():
    """Test setup_logger with debug=None sets INFO level (default logic)."""
    with patch.object(logger, "remove") as mock_remove, patch.object(logger, "add") as mock_add:
        setup_logger(debug=None)

        mock_remove.assert_called_once()

        calls = mock_add.call_args_list
        assert len(calls) == 2

        # First call: stdout handler with INFO level (since debug is falsy)
        stdout_call = calls[0]
        assert stdout_call[0][0] == sys.stdout
        assert stdout_call[1]["level"] == "INFO"

        # Second call: stderr handler with WARNING level
        stderr_call = calls[1]
        assert stderr_call[0][0] == sys.stderr
        assert stderr_call[1]["level"] == "WARNING"


def test_setup_logger_filter_function():
    """Test that the filter function in stdout handler correctly filters levels."""
    with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
        setup_logger()

        # Get the filter function from the first call (stdout handler)
        filter_func = mock_add.call_args_list[0][1]["filter"]

        # Test that levels with no < 30 pass (DEBUG=10, INFO=20)
        debug_record = {"level": type("Level", (), {"no": 10})}
        info_record = {"level": type("Level", (), {"no": 20})}
        warning_record = {"level": type("Level", (), {"no": 30})}
        error_record = {"level": type("Level", (), {"no": 40})}

        assert filter_func(debug_record) is True
        assert filter_func(info_record) is True
        assert filter_func(warning_record) is False
        assert filter_func(error_record) is False
