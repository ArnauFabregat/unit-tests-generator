from unittest.mock import patch

from utgen.main import run


def test_run_normal_with_graph_and_overwrite_false(tmp_path):
    src_path = tmp_path / "src"
    test_path = tmp_path / "tests"
    graph_path = tmp_path / "graph.json"
    with patch("utgen.main.pipeline") as mock_pipeline, patch("utgen.main.subprocess.run") as mock_subprocess:
        run(src_path, test_path, graph_path, overwrite=False)
        mock_pipeline.assert_called_once_with(
            source_code_dir=str(src_path),
            tests_output_dir=str(test_path),
            save_graph_path=str(graph_path),
            overwrite=False,
        )
        mock_subprocess.assert_called_once_with(
            ["pytest", str(test_path), f"--cov={src_path}", "--cov-report=term-missing"], check=True
        )


def test_run_normal_without_graph_and_overwrite_true(tmp_path):
    src_path = tmp_path / "src"
    test_path = tmp_path / "tests"
    graph_path = None
    with patch("utgen.main.pipeline") as mock_pipeline, patch("utgen.main.subprocess.run") as mock_subprocess:
        run(src_path, test_path, graph_path, overwrite=True)
        mock_pipeline.assert_called_once_with(
            source_code_dir=str(src_path), tests_output_dir=str(test_path), save_graph_path="", overwrite=True
        )
        mock_subprocess.assert_called_once_with(
            ["pytest", str(test_path), f"--cov={src_path}", "--cov-report=term-missing"], check=True
        )
