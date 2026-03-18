from pathlib import Path
from unittest.mock import patch


def test_run_with_all_paths_provided():
    """Test run function with all paths provided."""
    with (
        patch("utgen.main.pipeline") as mock_pipeline,
        patch("utgen.main.subprocess.run") as mock_subprocess,
        patch("utgen.main.logger") as mock_logger,
    ):
        src_path = Path("/test/source")
        test_path = Path("/test/tests")
        graph_path = Path("/test/graph.json")

        from utgen.main import run

        run(src_path, test_path, graph_path)

        mock_pipeline.assert_called_once_with(
            source_code_dir=str(src_path), tests_output_dir=str(test_path), save_graph_path=str(graph_path)
        )

        mock_subprocess.assert_called_once_with(
            ["pytest", str(test_path), f"--cov={src_path}", "--cov-report=term-missing"], check=True
        )

        mock_logger.info.assert_any_call("Initializing utgen...")
        mock_logger.info.assert_any_call(f"Source: {src_path} | Tests: {test_path} | Graph: {graph_path}")
        mock_logger.info.assert_any_call("Running coverage report...")


def test_run_with_no_graph_path():
    """Test run function with graph_path=None."""
    with patch("utgen.main.pipeline") as mock_pipeline, patch("utgen.main.subprocess.run") as mock_subprocess:
        src_path = Path("/test/source")
        test_path = Path("/test/tests")

        from utgen.main import run

        run(src_path, test_path, None)

        mock_pipeline.assert_called_once_with(
            source_code_dir=str(src_path), tests_output_dir=str(test_path), save_graph_path=""
        )

        mock_subprocess.assert_called_once()


def test_run_when_subprocess_fails():
    """Test run function when subprocess.CalledProcessError is raised."""
    with (
        patch("utgen.main.pipeline"),
        patch("utgen.main.logger") as mock_logger,
    ):
        src_path = Path("/test/source")
        test_path = Path("/test/tests")

        from utgen.main import run

        run(src_path, test_path)

        mock_logger.warning.assert_called_once_with("Some tests failed or coverage couldn't be calculated.")
