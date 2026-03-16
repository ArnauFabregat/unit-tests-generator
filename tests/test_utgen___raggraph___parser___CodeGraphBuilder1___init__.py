from unittest.mock import MagicMock, patch

from utgen.raggraph.parser import CodeGraphBuilder1
from utgen.raggraph.utils import canonical_id


@patch("builtins.open")
def test_codegraphbuilder1_init_with_different_paths(mock_open):
    mock_graph = MagicMock()
    code_path = "/home/user/project/src"
    file_path = "/home/user/project/src/subdir/file.py"

    mock_file_content = b"class MyClass:\n    pass"
    mock_open.return_value.__enter__.return_value.read.return_value = mock_file_content

    builder = CodeGraphBuilder1(code_path, file_path, mock_graph)

    assert builder.file_path_clean == "subdir/file.py"
    assert builder.current_file_id == canonical_id("subdir/file.py")

    mock_graph.add_node.assert_called_once()
    call_args = mock_graph.add_node.call_args[1]
    assert call_args["name"] == "file.py"
    assert call_args["file"] == "subdir/file.py"
