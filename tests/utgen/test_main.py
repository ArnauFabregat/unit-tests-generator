from unittest.mock import patch

from utgen.main import run


def test_run_with_valid_paths(tmp_path):
    """
    Test run function with valid source and test paths.
    """
    # Arrange
    src_path = tmp_path / "src"
    src_path.mkdir()
    test_path = tmp_path / "tests"
    test_path.mkdir()
    graph_path = tmp_path / "graph.json"

    # Mock the pipeline function
    with patch("utgen.main.pipeline") as mock_pipeline:
        # Act
        run(src_path, test_path, graph_path)

        # Assert
        mock_pipeline.assert_called_once_with(
            source_code_dir=str(src_path), tests_output_dir=str(test_path), save_graph_path=str(graph_path)
        )


def test_run_without_graph_path(tmp_path):
    """
    Test run function without providing a graph path.
    """
    # Arrange
    src_path = tmp_path / "src"
    src_path.mkdir()
    test_path = tmp_path / "tests"
    test_path.mkdir()

    # Mock the pipeline function
    with patch("utgen.main.pipeline") as mock_pipeline:
        # Act
        run(src_path, test_path)

        # Assert
        mock_pipeline.assert_called_once_with(
            source_code_dir=str(src_path), tests_output_dir=str(test_path), save_graph_path=""
        )
