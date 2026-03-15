from unittest.mock import MagicMock, patch

from utgen.raggraph.parser import CodeGraphBuilder2


def test_code_graph_builder2_init_empty_source():
    graph = MagicMock()
    code_path = "test_code_path"
    file_path = "test_code_path/test_file.py"

    with patch("utgen.raggraph.utils.canonical_id", return_value="test_file_id") as mock_canonical:
        builder = CodeGraphBuilder2(code_path, file_path, graph)

        assert builder.dst_canonical_id is None
