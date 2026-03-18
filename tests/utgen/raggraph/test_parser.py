import ast
from unittest.mock import patch

import networkx as nx

from utgen.raggraph.parser import CodeGraphBuilder1, CodeGraphBuilder2


def test_code_graph_builder1_init_initializes_state_correctly(tmp_path):
    """Test that __init__ initializes all state variables correctly."""
    # Create a dummy file
    test_file = tmp_path / "dummy.py"
    test_file.write_text("# dummy")

    code_path = str(tmp_path)
    file_path = str(test_file)
    graph = nx.DiGraph()

    builder = CodeGraphBuilder1(code_path, file_path, graph)

    # Verify all instance variables are set to expected initial values
    assert hasattr(builder, "file_path")
    assert hasattr(builder, "file_path_clean")
    assert hasattr(builder, "graph")
    assert hasattr(builder, "current_file_id")
    assert hasattr(builder, "current_class")
    assert hasattr(builder, "function_stack")
    assert hasattr(builder, "current_scope")

    # Verify initial values
    assert builder.current_class is None
    assert isinstance(builder.function_stack, list)
    assert len(builder.function_stack) == 0
    assert builder.current_scope is None
    assert isinstance(graph, nx.DiGraph)


def test_code_graph_builder2_init_initializes_state_variables(tmp_path):
    """Test that __init__ initializes all state variables correctly."""
    # Create a dummy file
    test_file = tmp_path / "dummy.py"
    test_file.write_text("# dummy")

    code_path = str(tmp_path)
    file_path = str(test_file)
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)

    # Verify all instance variables are set
    assert hasattr(builder, "file_path")
    assert hasattr(builder, "file_path_clean")
    assert hasattr(builder, "graph")
    assert hasattr(builder, "current_file_id")
    assert hasattr(builder, "current_class")
    assert hasattr(builder, "function_stack")
    assert hasattr(builder, "current_scope")
    assert hasattr(builder, "dst_canonical_id")

    # Verify initial values
    assert builder.current_class is None
    assert isinstance(builder.function_stack, list)
    assert len(builder.function_stack) == 0
    assert builder.current_scope is None
    assert builder.dst_canonical_id is None


def test_code_graph_builder2_init_with_different_canonical_id():
    """Test CodeGraphBuilder2.__init__ with mocked canonical_id."""
    # Mock canonical_id to return a specific value
    with patch("utgen.raggraph.parser.canonical_id", return_value="custom::file::id") as mock_canonical:
        code_path = "/test"
        file_path = "/test/module.py"
        graph = nx.DiGraph()

        from utgen.raggraph.parser import CodeGraphBuilder2

        builder = CodeGraphBuilder2(code_path, file_path, graph)

        # Check that canonical_id was called with the correct argument
        mock_canonical.assert_called_once_with("module.py")

        # Check that current_file_id uses the mocked value
        assert builder.current_file_id == "custom::file::id"

        # Other attributes should be set correctly
        assert builder.file_path == file_path
        assert builder.file_path_clean == "module.py"
        assert builder.graph is graph


def test_attach_parents_with_simple_ast():
    """
    Test attach_parents with a simple AST containing a FunctionDef.
    """
    # Arrange
    fn_node = ast.FunctionDef(
        name="my_function",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    CodeGraphBuilder2.attach_parents(fn_node)

    # Assert
    # Verify that the FunctionDef node has no parent (it's the root)
    assert not hasattr(fn_node, "parent")

    # Verify that child nodes have the parent attribute set
    # In this case, FunctionDef has no child nodes, so nothing to check
    assert True


def test_attach_parents_with_nested_structure():
    """Test attach_parents with a nested AST structure."""
    # Arrange
    # Create a simple module with a function that has a return statement
    module = ast.Module(body=[ast.Return(value=ast.Constant(value=42))])
    ast.fix_missing_locations(module)

    # Act
    CodeGraphBuilder2.attach_parents(module)

    # Assert
    # The module (root) should have no parent
    assert not hasattr(module, "parent")

    # The return node should have the module as parent
    return_node = module.body[0]
    assert hasattr(return_node, "parent")
    assert return_node.parent is module

    # The constant node should have the return node as parent
    constant_node = return_node.value
    assert hasattr(constant_node, "parent")
    assert constant_node.parent is return_node


def test_attach_parents_with_empty_ast():
    """Test attach_parents with an empty AST (Module with no body)."""
    # Arrange
    module = ast.Module(body=[])
    ast.fix_missing_locations(module)

    # Act
    CodeGraphBuilder2.attach_parents(module)

    # Assert
    # The module should have no parent
    assert not hasattr(module, "parent")
    # No children to check
    assert module.body == []


def test_attach_parents_with_multiple_children():
    """Test attach_parents with a node that has multiple children."""
    # Arrange
    # Create a FunctionDef with two statements in its body
    fn_node = ast.FunctionDef(
        name="my_function",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[ast.Pass(), ast.Return(value=None)],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )
    ast.fix_missing_locations(fn_node)

    # Act
    CodeGraphBuilder2.attach_parents(fn_node)

    # Assert
    # The function node should have no parent
    assert not hasattr(fn_node, "parent")

    # Each statement in the body should have the function node as parent
    for stmt in fn_node.body:
        assert hasattr(stmt, "parent")
        assert stmt.parent is fn_node
        # The Return statement has a child (None), but we don't need to check recursively here
        # because the method is recursive and would have set the parent for the Constant node as well


def test_visit_classdef_basic_functionality():
    """Test visit_ClassDef sets and restores current_class state."""
    # Create a temporary file
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)

    # Create a ClassDef node
    class_node = ast.ClassDef(name="MyClass", bases=[], keywords=[], body=[ast.Pass()], decorator_list=[])

    # Track the previous class state
    prev_class = builder.current_class

    # Mock canonical_id to return a known value
    with patch("utgen.raggraph.parser.canonical_id") as mock_canonical:
        mock_canonical.return_value = "module.py::class::MyClass"

        # Call visit_ClassDef
        builder.visit_ClassDef(class_node)

        # Verify canonical_id was called with correct arguments
        mock_canonical.assert_called_once_with("module.py", "class", "MyClass")

        # After visit, current_class should be restored to previous value (None)
        assert builder.current_class == prev_class


def test_visit_classdef_with_real_canonical_id():
    """Test visit_ClassDef with real canonical_id function."""
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)

    # Create a ClassDef node
    class_node = ast.ClassDef(name="AnotherClass", bases=[], keywords=[], body=[ast.Pass()], decorator_list=[])

    # Store initial state
    initial_class = builder.current_class

    # Call visit_ClassDef
    builder.visit_ClassDef(class_node)

    # After visit, current_class should be restored to initial state
    assert builder.current_class == initial_class

    # The method should have called generic_visit, but we can't test that directly
    # without analyzing the entire visitor pattern


def test_visit_classdef_state_management():
    """Test visit_ClassDef properly manages current_class state."""
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)

    # Set an initial current_class to test state preservation
    builder.current_class = "module.py::class::ExistingClass"

    # Create a ClassDef node
    class_node = ast.ClassDef(name="NewClass", bases=[], keywords=[], body=[ast.Pass()], decorator_list=[])

    # Mock generic_visit to avoid traversing the entire AST
    with (
        patch.object(builder, "generic_visit") as mock_generic,
        patch("utgen.raggraph.parser.canonical_id") as mock_canonical,
    ):
        mock_canonical.return_value = "module.py::class::NewClass"

        builder.visit_ClassDef(class_node)

        # generic_visit should be called
        mock_generic.assert_called_once_with(class_node)

        # After visit, current_class should be restored to the original value
        assert builder.current_class == "module.py::class::ExistingClass"


def test_visit_classdef_with_empty_class():
    """Test visit_ClassDef with an empty class (no body)."""
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)

    # Create an empty ClassDef node
    class_node = ast.ClassDef(
        name="EmptyClass",
        bases=[],
        keywords=[],
        body=[],  # Empty body
        decorator_list=[],
    )

    # Track initial state
    initial_class = builder.current_class

    builder.visit_ClassDef(class_node)

    # current_class should be restored to initial state
    assert builder.current_class == initial_class

    # Even with empty body, generic_visit would be called and should handle empty list
    # This ensures no errors occur with empty classes


def test_visit_functiondef_top_level_function():
    """Test visit_FunctionDef with a top-level function."""
    # Setup
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)

    # Create a FunctionDef node
    func_node = ast.FunctionDef(
        name="my_function",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[ast.Pass()],
        decorator_list=[],
    )

    # Mock dependencies
    with (
        patch("utgen.raggraph.parser.canonical_id") as mock_canonical,
        patch.object(builder, "generic_visit") as mock_generic_visit,
    ):
        mock_canonical.return_value = "module.py::function::my_function"

        # Act
        builder.visit_FunctionDef(func_node)

        # Assert
        mock_canonical.assert_called_once_with("module.py", "function", "my_function")
        mock_generic_visit.assert_called_once_with(func_node)

        # Check state management
        assert len(builder.function_stack) == 0  # Function popped after visit
        assert builder.current_scope is None  # Scope restored


def test_visit_functiondef_method():
    """Test visit_FunctionDef with a method inside a class."""
    # Setup
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)
    builder.current_class = "module.py::class::MyClass"  # Simulate being inside a class

    # Create a FunctionDef node
    func_node = ast.FunctionDef(
        name="my_method",
        args=ast.arguments(
            args=[ast.arg(arg="self")], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=[ast.Pass()],
        decorator_list=[],
    )

    with (
        patch("utgen.raggraph.parser.canonical_id") as mock_canonical,
        patch.object(builder, "generic_visit") as mock_generic_visit,
    ):
        mock_canonical.return_value = "module.py::method::MyClass.my_method"

        # Act
        builder.visit_FunctionDef(func_node)

        # Assert
        mock_canonical.assert_called_once_with("module.py", "method", "MyClass.my_method")
        mock_generic_visit.assert_called_once_with(func_node)

        # Check state management
        assert len(builder.function_stack) == 0  # Popped after visit
        assert builder.current_scope is None
        # current_class should remain unchanged
        assert builder.current_class == "module.py::class::MyClass"


def test_visit_functiondef_nested_function():
    """Test visit_FunctionDef with a nested function inside another function."""
    # Setup
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)
    builder.function_stack.append("module.py::function::outer")  # Simulate being inside outer function

    # Create a FunctionDef node for inner function
    func_node = ast.FunctionDef(
        name="inner",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[ast.Pass()],
        decorator_list=[],
    )

    with (
        patch("utgen.raggraph.parser.canonical_id") as mock_canonical,
        patch.object(builder, "generic_visit") as mock_generic_visit,
    ):
        mock_canonical.return_value = "module.py::nested_function::outer.inner"

        # Act
        builder.visit_FunctionDef(func_node)

        # Assert
        mock_canonical.assert_called_once_with("module.py", "nested_function", "outer.inner")
        mock_generic_visit.assert_called_once_with(func_node)

        # Check state management
        # After visit, function stack should have popped the inner function and restored the outer function
        assert len(builder.function_stack) == 1
        assert builder.function_stack[0] == "module.py::function::outer"
        assert builder.current_scope is None  # Restored to None (since we didn't set a current_scope before)


def test_visit_functiondef_state_restoration():
    """Test that visit_FunctionDef properly restores state after visiting."""
    # Setup
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)

    # Simulate initial state
    builder.function_stack = ["module.py::function::initial"]
    builder.current_scope = "module.py::function::initial"

    # Create a FunctionDef node
    func_node = ast.FunctionDef(
        name="another",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[ast.Pass()],
        decorator_list=[],
    )

    with (
        patch("utgen.raggraph.parser.canonical_id") as mock_canonical,
        patch.object(builder, "generic_visit") as mock_generic_visit,
    ):
        mock_canonical.return_value = "module.py::function::another"

        # Act
        builder.visit_FunctionDef(func_node)

        # Assert
        # After visit, the initial state should be restored
        assert builder.function_stack == ["module.py::function::initial"]
        assert builder.current_scope == "module.py::function::initial"
        # generic_visit should have been called
        mock_generic_visit.assert_called_once_with(func_node)


def test_visit_async_function_def_with_real_implementation():
    """Test visit_AsyncFunctionDef with real visit_FunctionDef implementation."""
    # Setup
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)

    # Create an AsyncFunctionDef node
    async_node = ast.AsyncFunctionDef(
        name="async_method",
        args=ast.arguments(
            args=[ast.arg(arg="self")], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=[ast.Pass()],
        decorator_list=[],
    )

    # We'll mock generic_visit to avoid traversing the entire AST
    with (
        patch.object(builder, "generic_visit") as mock_generic,
        patch("utgen.raggraph.parser.canonical_id") as mock_canonical,
    ):
        mock_canonical.return_value = "module.py::function::async_method"

        # Act
        builder.visit_AsyncFunctionDef(async_node)

        # Assert that visit_FunctionDef was called (which in turn calls generic_visit)
        # Since we're calling the real visit_FunctionDef, it will call generic_visit
        mock_generic.assert_called_once_with(async_node)
        mock_canonical.assert_called_once_with("module.py", "function", "async_method")

        # Check state management
        assert len(builder.function_stack) == 0
        assert builder.current_scope is None


def test_visit_async_function_def_in_class():
    """Test visit_AsyncFunctionDef with an async method in a class."""
    # Setup
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)
    builder.current_class = "module.py::class::MyClass"

    # Create an AsyncFunctionDef node
    async_node = ast.AsyncFunctionDef(
        name="async_method",
        args=ast.arguments(
            args=[ast.arg(arg="self")], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=[ast.Pass()],
        decorator_list=[],
    )

    with (
        patch.object(builder, "generic_visit") as mock_generic,
        patch("utgen.raggraph.parser.canonical_id") as mock_canonical,
    ):
        mock_canonical.return_value = "module.py::method::MyClass.async_method"

        # Act
        builder.visit_AsyncFunctionDef(async_node)

        # Assert
        mock_canonical.assert_called_once_with("module.py", "method", "MyClass.async_method")
        mock_generic.assert_called_once_with(async_node)

        # Check state management
        assert builder.current_class == "module.py::class::MyClass"  # Should remain unchanged
        assert len(builder.function_stack) == 0  # Popped after visit
        assert builder.current_scope is None


def test_visit_async_function_def_nested():
    """Test visit_AsyncFunctionDef with nested async function."""
    # Setup
    code_path = "/test"
    file_path = "/test/module.py"
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    builder = CodeGraphBuilder2(code_path, file_path, graph)
    builder.function_stack.append("module.py::function::outer")

    # Create an AsyncFunctionDef node
    async_node = ast.AsyncFunctionDef(
        name="inner_async",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[ast.Pass()],
        decorator_list=[],
    )

    with (
        patch.object(builder, "generic_visit") as mock_generic,
        patch("utgen.raggraph.parser.canonical_id") as mock_canonical,
    ):
        mock_canonical.return_value = "module.py::nested_function::outer.inner_async"

        # Act
        builder.visit_AsyncFunctionDef(async_node)

        # Assert
        mock_canonical.assert_called_once_with("module.py", "nested_function", "outer.inner_async")
        mock_generic.assert_called_once_with(async_node)

        # Check state management
        assert len(builder.function_stack) == 1  # outer function remains
        assert builder.function_stack[0] == "module.py::function::outer"
        assert builder.current_scope is None  # Restored to None


def test_is_local_symbol_found():
    """Test is_local_symbol returns True and sets dst_canonical_id when symbol found."""
    # Create a graph with nodes
    graph = nx.DiGraph()
    graph.add_node("file.py::function::hello", name="hello", type="function")
    graph.add_node("file.py::class::MyClass", name="MyClass", type="class")

    from utgen.raggraph.parser import CodeGraphBuilder2

    # We'll mock the initialization to avoid file operations
    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph
        builder.dst_canonical_id = None

        # Test finding existing symbol
        result = builder.is_local_symbol("hello")

        assert result is True
        assert builder.dst_canonical_id == "file.py::function::hello"

        # Test finding another existing symbol
        result = builder.is_local_symbol("MyClass")

        assert result is True
        assert builder.dst_canonical_id == "file.py::class::MyClass"


def test_is_local_symbol_not_found():
    """Test is_local_symbol returns False when symbol not found."""
    # Create a graph without the target symbol
    graph = nx.DiGraph()
    graph.add_node("file.py::function::hello", name="hello", type="function")

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph
        builder.dst_canonical_id = None

        # Test not finding symbol
        result = builder.is_local_symbol("nonexistent")

        assert result is False
        # dst_canonical_id should remain unchanged (None)
        assert builder.dst_canonical_id is None


def test_is_local_symbol_with_empty_graph():
    """Test is_local_symbol with an empty graph."""
    graph = nx.DiGraph()  # Empty graph

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph
        builder.dst_canonical_id = None

        result = builder.is_local_symbol("any_name")

        assert result is False
        assert builder.dst_canonical_id is None


def test_is_local_symbol_updates_dst_canonical_id_on_successive_calls():
    """Test that dst_canonical_id is updated correctly on successive calls."""
    graph = nx.DiGraph()
    graph.add_node("id1", name="symbol1", type="function")
    graph.add_node("id2", name="symbol2", type="function")

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph
        builder.dst_canonical_id = "initial"

        # First call: find symbol1
        result1 = builder.is_local_symbol("symbol1")
        assert result1 is True
        assert builder.dst_canonical_id == "id1"

        # Second call: find symbol2
        result2 = builder.is_local_symbol("symbol2")
        assert result2 is True
        assert builder.dst_canonical_id == "id2"

        # Third call: symbol not found, dst_canonical_id should remain unchanged
        result3 = builder.is_local_symbol("symbol3")
        assert result3 is False
        assert builder.dst_canonical_id == "id2"  # Still from previous successful call


def test_visit_name_no_current_scope():
    """Test visit_Name returns early when current_scope is None."""
    # Create builder with empty graph
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph
        builder.current_scope = None  # No current scope

        # Create a Name node
        name_node = ast.Name(id="some_func")

        # Act
        builder.visit_Name(name_node)

        # Assert - no edges should be added since we returned early
        assert len(graph.edges()) == 0


def test_visit_name_call_detection():
    """Test visit_Name detects when a name is being called."""
    # Create builder with graph containing nodes
    graph = nx.DiGraph()
    graph.add_node("module.py::function::my_func", name="my_func", type="function")
    graph.add_node("module.py::function::caller", name="caller", type="function")

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph
        builder.current_scope = "module.py::function::caller"
        builder.dst_canonical_id = None

        # Create a Name node that will be inside a Call
        name_node = ast.Name(id="my_func")
        call_node = ast.Call(func=name_node, args=[], keywords=[])

        # Attach parent so visit_Name can detect the Call relationship
        name_node.parent = call_node

        # Act
        builder.visit_Name(name_node)

        # Assert - should add a "calls" edge
        assert graph.has_edge("module.py::function::caller", "module.py::function::my_func")
        assert graph.edges["module.py::function::caller", "module.py::function::my_func"]["rel"] == "calls"


def test_visit_name_reference_detection():
    """Test visit_Name detects when a name is referenced (not called)."""
    # Create builder with graph containing nodes
    graph = nx.DiGraph()
    graph.add_node("module.py::class::MyClass", name="MyClass", type="class")
    graph.add_node("module.py::function::my_func", name="my_func", type="function")

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph
        builder.current_scope = "module.py::function::my_func"
        builder.dst_canonical_id = None

        # Create a Name node used as a reference (e.g., in an assignment or return)
        name_node = ast.Name(id="MyClass")

        # Attach a non-Call parent (e.g., a Return node)
        return_node = ast.Return(value=name_node)
        name_node.parent = return_node

        # Act
        builder.visit_Name(name_node)

        # Assert - should add a "references" edge
        assert graph.has_edge("module.py::function::my_func", "module.py::class::MyClass")
        assert graph.edges["module.py::function::my_func", "module.py::class::MyClass"]["rel"] == "references"


def test_visit_name_symbol_not_found():
    """Test visit_Name doesn't add edges when symbol not found in graph."""
    # Create builder with graph that doesn't contain the target symbol
    graph = nx.DiGraph()
    graph.add_node("module.py::function::existing", name="existing", type="function")

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph
        builder.current_scope = "module.py::function::existing"
        builder.dst_canonical_id = None

        # Create a Name node for a non-existent symbol
        name_node = ast.Name(id="nonexistent")

        # Attach a Return parent
        return_node = ast.Return(value=name_node)
        name_node.parent = return_node

        # Act
        builder.visit_Name(name_node)

        # Assert - no edges should be added since symbol not found
        assert len(graph.edges()) == 0
        assert builder.dst_canonical_id is None


def test_visit_call_simple_function_no_args():
    """Test visit_Call with a simple function call with no arguments."""
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph

        # Create a simple call: my_func()
        func_name = ast.Name(id="my_func")
        call_node = ast.Call(func=func_name, args=[], keywords=[])

        # Mock the visit method to track calls
        with patch.object(builder, "visit") as mock_visit:
            # Act
            builder.visit_Call(call_node)

            # Assert - visit should be called once for the func only
            mock_visit.assert_called_once_with(func_name)


def test_visit_call_with_positional_arguments():
    """Test visit_Call with positional arguments."""
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph

        # Create a call with arguments: my_func(arg1, arg2)
        func_name = ast.Name(id="my_func")
        arg1 = ast.Name(id="arg1")
        arg2 = ast.Name(id="arg2")
        call_node = ast.Call(func=func_name, args=[arg1, arg2], keywords=[])

        with patch.object(builder, "visit") as mock_visit:
            # Act
            builder.visit_Call(call_node)

            # Assert - visit should be called for func, arg1, arg2
            assert mock_visit.call_count == 3
            mock_visit.assert_any_call(func_name)
            mock_visit.assert_any_call(arg1)
            mock_visit.assert_any_call(arg2)


def test_visit_call_with_keyword_arguments():
    """Test visit_Call with keyword arguments."""
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph

        # Create a call with keyword arguments: my_func(a=1, b=expr)
        func_name = ast.Name(id="my_func")
        kw_value = ast.Name(id="some_expr")
        keyword = ast.keyword(arg="b", value=kw_value)
        call_node = ast.Call(func=func_name, args=[], keywords=[keyword])

        with patch.object(builder, "visit") as mock_visit:
            # Act
            builder.visit_Call(call_node)

            # Assert - visit should be called for func and keyword value
            assert mock_visit.call_count == 2
            mock_visit.assert_any_call(func_name)
            mock_visit.assert_any_call(kw_value)


def test_visit_call_with_mixed_arguments():
    """Test visit_Call with both positional and keyword arguments."""
    graph = nx.DiGraph()

    from utgen.raggraph.parser import CodeGraphBuilder2

    with patch.object(CodeGraphBuilder2, "__init__", lambda self, *args: None):
        builder = CodeGraphBuilder2()
        builder.graph = graph

        # Create a call: my_func(pos1, pos2, kw1=val1, kw2=val2)
        func_name = ast.Name(id="my_func")
        pos1 = ast.Constant(value=1)
        pos2 = ast.Name(id="x")
        kw1_value = ast.Constant(value="hello")
        kw2_value = ast.Name(id="y")

        keyword1 = ast.keyword(arg="kw1", value=kw1_value)
        keyword2 = ast.keyword(arg="kw2", value=kw2_value)

        call_node = ast.Call(func=func_name, args=[pos1, pos2], keywords=[keyword1, keyword2])

        with patch.object(builder, "visit") as mock_visit:
            # Act
            builder.visit_Call(call_node)

            # Assert - visit should be called for: func, pos1, pos2, kw1_value, kw2_value
            assert mock_visit.call_count == 5
            mock_visit.assert_any_call(func_name)
            mock_visit.assert_any_call(pos1)
            mock_visit.assert_any_call(pos2)
            mock_visit.assert_any_call(kw1_value)
            mock_visit.assert_any_call(kw2_value)
