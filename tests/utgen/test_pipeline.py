import json
from unittest.mock import MagicMock, patch

import networkx as nx


def test_pipeline_with_function_nodes_success():
    """Test pipeline successfully generates tests for function nodes."""
    # Create a mock graph with function nodes
    mock_graph = MagicMock(spec=nx.DiGraph)
    mock_graph.number_of_nodes.return_value = 3
    mock_graph.number_of_edges.return_value = 2
    mock_graph.nodes.return_value = [
        ("utgen/logger.py::function::setup_logger", {"type": "function", "file": "utgen/logger.py"}),
    ]

    # Mock the test generation response
    mock_response = MagicMock()
    mock_response.raw = json.dumps(
        {"tests": {"test_setup_logger": {"imports": ["import pytest"], "code": "def test_setup_logger(): pass"}}}
    )

    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = mock_response

    with (
        patch("utgen.pipeline.build_graph_from_directory", return_value=mock_graph),
        patch("utgen.pipeline.TestGenerationCrew") as mock_crew_class,
        patch("utgen.pipeline.get_node_context", return_value="test context"),
        patch("utgen.pipeline.validate_individual_test", return_value=True),
        patch("utgen.pipeline.save_and_clean_tests") as mock_save,
    ):
        mock_crew_class.return_value.crew.return_value = mock_crew_instance

        from utgen.pipeline import pipeline

        pipeline(source_code_dir="/src", tests_output_dir="/tests", save_graph_path="/graph.graphml")

        mock_save.assert_called_once()


def test_pipeline_handles_generation_error():
    """Test pipeline continues when test generation fails for a node."""
    mock_graph = MagicMock(spec=nx.DiGraph)
    mock_graph.number_of_nodes.return_value = 2
    mock_graph.number_of_edges.return_value = 1
    mock_graph.nodes.return_value = [
        ("utgen/logger.py::function::setup_logger", {"type": "function", "file": "utgen/logger.py"}),
        ("utgen/utils.py::function::helper", {"type": "function", "file": "utgen/utils.py"}),
    ]

    # First call succeeds, second fails
    mock_response = MagicMock()
    mock_response.raw = json.dumps({"tests": {"test_func": {"imports": [], "code": "pass"}}})

    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.side_effect = [mock_response, json.JSONDecodeError("test", "test", 0)]

    with (
        patch("utgen.pipeline.build_graph_from_directory", return_value=mock_graph),
        patch("utgen.pipeline.TestGenerationCrew") as mock_crew_class,
        patch("utgen.pipeline.get_node_context", return_value="context"),
        patch("utgen.pipeline.validate_individual_test", return_value=True),
        patch("utgen.pipeline.save_and_clean_tests") as mock_save,
    ):
        mock_crew_class.return_value.crew.return_value = mock_crew_instance

        from utgen.pipeline import pipeline

        # Should not raise exception despite one node failing
        pipeline(source_code_dir="/src", tests_output_dir="/tests")

        mock_save.assert_called_once()


def test_pipeline_with_empty_graph_path():
    """Test pipeline with empty save_graph_path (default)."""
    mock_graph = MagicMock(spec=nx.DiGraph)
    mock_graph.number_of_nodes.return_value = 0
    mock_graph.number_of_edges.return_value = 0
    mock_graph.nodes.return_value = []

    with (
        patch("utgen.pipeline.build_graph_from_directory", return_value=mock_graph) as mock_build,
        patch("utgen.pipeline.save_and_clean_tests"),
    ):
        from utgen.pipeline import pipeline

        pipeline(source_code_dir="/src", tests_output_dir="/tests")

        # Verify build_graph_from_directory called with empty save_graph_path
        mock_build.assert_called_once_with(code_path="/src", save_graph_path="")
