import ast
from unittest.mock import MagicMock

import networkx as nx

from utgen.raggraph.parser import CodeGraphBuilder2


def test_visit_name_with_no_current_scope(tmp_path):
    """
    Test visit_Name when current_scope is None.
    """
    # Arrange
    file_path = tmp_path / "test_file.py"
    file_path.write_text('print("Hello")')

    graph = nx.DiGraph()

    # Create a mock builder with initialized state
    builder = MagicMock(spec=CodeGraphBuilder2)
    builder.graph = graph
    builder.current_scope = None
    builder.dst_canonical_id = None

    # Create AST nodes
    name_node = ast.Name(id="print", ctx=ast.Load())

    # Act
    builder.visit_Name(name_node)

    # Assert
    # Verify that the method returned early
    assert not builder.is_local_symbol.called
    assert not graph.number_of_edges()
