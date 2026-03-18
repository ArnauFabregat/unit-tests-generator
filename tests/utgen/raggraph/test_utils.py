import ast

from utgen.raggraph.utils import canonical_id, get_source_segment, normalize_signature


def test_get_source_segment_success(tmp_path):
    """Test get_source_segment extracts source correctly."""
    # Create a Python file with known content
    test_file = tmp_path / "module.py"
    test_file.write_text("def my_function():\n    return 42\n")

    # Parse the file and get a FunctionDef node
    with open(test_file) as f:
        tree = ast.parse(f.read())

    func_node = tree.body[0]  # The function definition

    result = get_source_segment(str(test_file), func_node)

    assert "def my_function():" in result
    assert "return 42" in result


def test_get_source_segment_missing_file():
    """Test get_source_segment returns empty string for missing file."""
    # Create a dummy AST node
    node = ast.Constant(value=42)
    node.lineno = 1
    node.end_lineno = 1

    result = get_source_segment("/nonexistent/path.py", node)

    assert result == ""


def test_get_source_segment_without_line_info(tmp_path):
    """Test get_source_segment returns empty string when node has no line info."""
    # Create a Python file
    test_file = tmp_path / "module.py"
    test_file.write_text("x = 42\n")

    # Create a node without lineno/end_lineno
    node = ast.Constant(value=42)

    result = get_source_segment(str(test_file), node)

    assert result == ""


def test_get_source_segment_multiline_class(tmp_path):
    """Test get_source_segment with a multiline class definition."""
    # Create a Python file with a class
    test_file = tmp_path / "module.py"
    test_file.write_text("class MyClass:\n    def method(self):\n        pass\n")

    # Parse and get the class node
    with open(test_file) as f:
        tree = ast.parse(f.read())

    class_node = tree.body[0]  # The class definition

    result = get_source_segment(str(test_file), class_node)

    assert "class MyClass:" in result
    assert "def method(self):" in result
    assert "pass" in result


def test_canonical_id_single_part():
    """Test canonical_id with a single part (file path)."""
    result = canonical_id("module.py")
    assert result == "module.py"

    # Another example
    result = canonical_id("package/submodule.py")
    assert result == "package/submodule.py"


def test_canonical_id_three_parts_class():
    """Test canonical_id with three parts for a class ID."""
    result = canonical_id("module.py", "class", "MyClass")
    assert result == "module.py::class::MyClass"

    # Another example
    result = canonical_id("pkg/utils.py", "class", "Helper")
    assert result == "pkg/utils.py::class::Helper"


def test_canonical_id_three_parts_function():
    """Test canonical_id with three parts for function/method ID."""
    # Top-level function
    result = canonical_id("module.py", "function", "my_function")
    assert result == "module.py::function::my_function"

    # Method
    result = canonical_id("module.py", "method", "MyClass.my_method")
    assert result == "module.py::method::MyClass.my_method"

    # Nested function
    result = canonical_id("module.py", "nested_function", "outer.inner")
    assert result == "module.py::nested_function::outer.inner"


def test_canonical_id_multiple_parts():
    """Test canonical_id with varying number of parts."""
    # Two parts
    result = canonical_id("package", "module")
    assert result == "package::module"

    # Four parts
    result = canonical_id("pkg", "module", "class", "method")
    assert result == "pkg::module::class::method"

    # Five parts
    result = canonical_id("a", "b", "c", "d", "e")
    assert result == "a::b::c::d::e"

    # Empty string parts (edge case)
    result = canonical_id("", "class", "MyClass")
    assert result == "::class::MyClass"


def test_normalize_signature_simple_function():
    """Test normalize_signature with a simple function with no arguments."""
    # Parse a simple function
    code = "def my_function(): pass"
    tree = ast.parse(code)
    func_node = tree.body[0]

    result = normalize_signature(func_node)

    assert result == "def my_function()"


def test_normalize_signature_async_function():
    """Test normalize_signature with an async function."""
    # Parse an async function
    code = "async def fetch_data(url: str) -> bytes: pass"
    tree = ast.parse(code)
    async_node = tree.body[0]

    result = normalize_signature(async_node)

    assert result == "async def fetch_data(url: str) -> bytes"

    # Simple async function without types
    code2 = "async def simple(): pass"
    tree2 = ast.parse(code2)
    async_node2 = tree2.body[0]

    result2 = normalize_signature(async_node2)

    assert result2 == "async def simple()"


def test_normalize_signature_with_args_kwargs():
    """Test normalize_signature with *args and **kwargs."""
    # Parse a function with *args and **kwargs
    code = "def variadic(*args, **kwargs): pass"
    tree = ast.parse(code)
    func_node = tree.body[0]

    result = normalize_signature(func_node)

    assert result == "def variadic(*args, **kwargs)"

    # With annotations
    code2 = "def typed_variadic(*args: int, **kwargs: str) -> None: pass"
    tree2 = ast.parse(code2)
    func_node2 = tree2.body[0]

    result2 = normalize_signature(func_node2)

    assert result2 == "def typed_variadic(*args: int, **kwargs: str) -> None"
