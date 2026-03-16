import ast
from unittest.mock import Mock, patch

from utgen.raggraph.parser import CodeGraphBuilder2


def test_visit_Call_basic_function_call():
    """
    Test visit_Call with a basic function call.
    """
    # Arrange
    # Create a Call node: func()
    call_node = ast.Call(func=ast.Name(id="func", ctx=ast.Load()), args=[], keywords=[])

    # Mock the visit method to track calls
    with patch.object(CodeGraphBuilder2, "visit") as mock_visit:
        # Initialize the builder
        builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=Mock())

        # Act
        builder.visit_Call(call_node)

        # Assert
        # Verify that visit was called three times: func, args, keywords
        assert mock_visit.call_count == 1  # Only func is visited (no args or keywords)

        # Verify the specific calls
        mock_visit.assert_any_call(call_node.func)


def test_visit_Call_with_arguments():
    """
    Test visit_Call with a function call that has arguments.
    """
    # Arrange
    # Create a Call node: func(arg1, arg2)
    call_node = ast.Call(
        func=ast.Name(id="func", ctx=ast.Load()),
        args=[ast.Name(id="arg1", ctx=ast.Load()), ast.Name(id="arg2", ctx=ast.Load())],
        keywords=[],
    )

    # Mock the visit method to track calls
    with patch.object(CodeGraphBuilder2, "visit") as mock_visit:
        # Initialize the builder
        builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=Mock())

        # Act
        builder.visit_Call(call_node)

        # Assert
        # Verify that visit was called three times: func, arg1, arg2
        assert mock_visit.call_count == 3

        # Verify the specific calls
        mock_visit.assert_any_call(call_node.func)
        mock_visit.assert_any_call(call_node.args[0])
        mock_visit.assert_any_call(call_node.args[1])


def test_visit_Call_with_keyword_arguments():
    """
    Test visit_Call with a function call that has keyword arguments.
    """
    # Arrange
    # Create a Call node: func(arg1=arg2)
    call_node = ast.Call(
        func=ast.Name(id="func", ctx=ast.Load()),
        args=[],
        keywords=[ast.keyword(arg="arg1", value=ast.Name(id="arg2", ctx=ast.Load()))],
    )

    # Mock the visit method to track calls
    with patch.object(CodeGraphBuilder2, "visit") as mock_visit:
        # Initialize the builder
        builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=Mock())

        # Act
        builder.visit_Call(call_node)

        # Assert
        # Verify that visit was called three times: func, arg2
        assert mock_visit.call_count == 2

        # Verify the specific calls
        mock_visit.assert_any_call(call_node.func)
        mock_visit.assert_any_call(call_node.keywords[0].value)


def test_visit_Call_with_class_constructor():
    """
    Test visit_Call with a class constructor call.
    """
    # Arrange
    # Create a Call node: MyClass()
    class_call = ast.Call(func=ast.Name(id="MyClass", ctx=ast.Load()), args=[], keywords=[])

    # Mock the visit method to track calls
    with patch.object(CodeGraphBuilder2, "visit") as mock_visit:
        # Initialize the builder
        builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=Mock())

        # Act
        builder.visit_Call(class_call)

        # Assert
        # Verify that visit was called once: MyClass
        assert mock_visit.call_count == 1

        # Verify the specific call
        mock_visit.assert_any_call(class_call.func)


def test_visit_Call_with_no_arguments_or_keywords():
    """
    Test visit_Call with a call that has no arguments or keywords.
    """
    # Arrange
    # Create a Call node: func()
    call_node = ast.Call(func=ast.Name(id="func", ctx=ast.Load()), args=[], keywords=[])

    # Mock the visit method to track calls
    with patch.object(CodeGraphBuilder2, "visit") as mock_visit:
        # Initialize the builder
        builder = CodeGraphBuilder2(code_path="src", file_path="src/module.py", graph=Mock())

        # Act
        builder.visit_Call(call_node)

        # Assert
        # Verify that visit was called once: func
        assert mock_visit.call_count == 1

        # Verify the specific call
        mock_visit.assert_any_call(call_node.func)
