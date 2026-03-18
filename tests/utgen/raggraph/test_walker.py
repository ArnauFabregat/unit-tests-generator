from unittest.mock import patch

import networkx as nx

from utgen.raggraph.walker import build_graph_from_directory, iter_python_files


def test_iter_python_files_skip_init_true(tmp_path):
    """Test iter_python_files with skip_init=True skips __init__.py files."""
    # Create test files
    (tmp_path / "module.py").write_text("x = 1")
    (tmp_path / "__init__.py").write_text("")
    (tmp_path / "utils.py").write_text("def helper(): pass")

    files = list(iter_python_files(str(tmp_path), skip_init=True))

    # Should find module.py and utils.py, but NOT __init__.py
    assert len(files) == 2
    assert any("module.py" in f for f in files)
    assert any("utils.py" in f for f in files)
    assert not any("__init__.py" in f for f in files)


def test_iter_python_files_skip_init_false(tmp_path):
    """Test iter_python_files with skip_init=False includes __init__.py files."""
    # Create test files
    (tmp_path / "module.py").write_text("x = 1")
    (tmp_path / "__init__.py").write_text("")

    files = list(iter_python_files(str(tmp_path), skip_init=False))

    # Should find both module.py and __init__.py
    assert len(files) == 2
    assert any("module.py" in f for f in files)
    assert any("__init__.py" in f for f in files)


def test_iter_python_files_empty_directory(tmp_path):
    """Test iter_python_files with empty directory yields nothing."""
    # Empty directory - no files

    files = list(iter_python_files(str(tmp_path)))

    assert len(files) == 0


def test_iter_python_files_nested_directories(tmp_path):
    """Test iter_python_files finds files in nested directories."""
    # Create nested structure
    subdir = tmp_path / "subdir" / "nested"
    subdir.mkdir(parents=True)

    (tmp_path / "root.py").write_text("# root")
    (tmp_path / "subdir" / "level1.py").write_text("# level1")
    (subdir / "level2.py").write_text("# level2")
    (tmp_path / "subdir" / "__init__.py").write_text("")

    files = list(iter_python_files(str(tmp_path), skip_init=True))

    # Should find root.py, level1.py, level2.py (but not __init__.py)
    assert len(files) == 3
    assert any("root.py" in f for f in files)
    assert any("level1.py" in f for f in files)
    assert any("level2.py" in f for f in files)
    assert not any("__init__.py" in f for f in files)


def test_build_graph_from_directory_single_file(tmp_path):
    """Test build_graph_from_directory with a single Python file."""
    # Create a test Python file
    test_file = tmp_path / "module.py"
    test_file.write_text("""def hello():
    return 'world'

class MyClass:
    pass
""")

    # Mock the builders to verify they are called
    with (
        patch("utgen.raggraph.walker.CodeGraphBuilder1") as MockBuilder1,
        patch("utgen.raggraph.walker.CodeGraphBuilder2") as MockBuilder2,
        patch("utgen.raggraph.walker.iter_python_files", return_value=[str(test_file)]),
    ):
        mock_builder1 = MockBuilder1.return_value
        mock_builder2 = MockBuilder2.return_value

        # Act
        graph = build_graph_from_directory(str(tmp_path), skip_init=True)

        # Assert
        assert isinstance(graph, nx.DiGraph)

        # Check that builders were called once each
        MockBuilder1.assert_called_once()
        MockBuilder2.assert_called_once()

        # Check that the builders' visit methods were called
        mock_builder1.visit.assert_called_once()
        mock_builder2.attach_parents.assert_called_once()
        mock_builder2.visit.assert_called_once()
