import ast

from utgen.raggraph.utils import normalize_signature


def test_normalize_signature_with_basic_function():
    # Create a simple FunctionDef node
    node = ast.FunctionDef(
        name="example",
        args=ast.arguments(
            posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=[],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    result = normalize_signature(node)
    assert result == "def example()"


def test_normalize_signature_with_arguments():
    # Create a FunctionDef node with various arguments
    node = ast.FunctionDef(
        name="example",
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(arg="a", annotation=ast.Name(id="int", ctx=ast.Load())),
                ast.arg(arg="b", annotation=ast.Name(id="str", ctx=ast.Load())),
            ],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body=[],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    result = normalize_signature(node)
    assert result == "def example(a: int, b: str)"


def test_normalize_signature_with_return_type():
    # Create a FunctionDef node with a return type
    node = ast.FunctionDef(
        name="example",
        args=ast.arguments(
            posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=[],
        decorator_list=[],
        returns=ast.Name(id="bool", ctx=ast.Load()),
        type_comment=None,
    )

    result = normalize_signature(node)
    assert result == "def example() -> bool"


def test_normalize_signature_with_all_features():
    # Create a FunctionDef node with all possible features
    node = ast.FunctionDef(
        name="example",
        args=ast.arguments(
            posonlyargs=[ast.arg(arg="a", annotation=ast.Name(id="int", ctx=ast.Load()))],
            args=[ast.arg(arg="b", annotation=ast.Name(id="str", ctx=ast.Load()))],
            vararg=ast.arg(arg="args", annotation=ast.Name(id="tuple", ctx=ast.Load())),
            kwonlyargs=[ast.arg(arg="c", annotation=ast.Name(id="float", ctx=ast.Load()))],
            kw_defaults=[None],
            kwarg=ast.arg(arg="kwargs", annotation=ast.Name(id="dict", ctx=ast.Load())),
            defaults=[],
        ),
        body=[],
        decorator_list=[],
        returns=ast.Name(id="None", ctx=ast.Load()),
        type_comment=None,
    )

    result = normalize_signature(node)
    assert result == "def example(a: int, /, b: str, *args: tuple, c: float, **kwargs: dict) -> None"


def test_normalize_signature_with_invalid_node():
    # Pass an invalid node (not a FunctionDef or AsyncFunctionDef)
    node = ast.ClassDef(name="ExampleClass", bases=[], keywords=[], body=[], decorator_list=[])

    result = normalize_signature(node)
    assert result == ""
