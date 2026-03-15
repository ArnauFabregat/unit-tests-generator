import ast

from utgen.raggraph.utils import normalize_signature


def test_normalize_signature_basic_function():
    # Create a basic FunctionDef node
    node = ast.FunctionDef(
        name="test_func",
        args=ast.arguments(
            posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=[],
        decorator_list=[],
        returns=None,
    )

    # Test the function
    result = normalize_signature(node)
    assert result == "def test_func()"


def test_normalize_signature_with_annotations():
    # Create a FunctionDef node with annotations
    node = ast.FunctionDef(
        name="test_func",
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(arg="x", annotation=ast.Name(id="int", ctx=ast.Load())),
                ast.arg(arg="y", annotation=ast.Name(id="str", ctx=ast.Load())),
            ],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body=[],
        decorator_list=[],
        returns=ast.Name(id="bool", ctx=ast.Load()),
    )

    # Test the function
    result = normalize_signature(node)
    assert result == "def test_func(x: int, y: str) -> bool"


def test_normalize_signature_with_posonly_args():
    # Create a FunctionDef node with posonly args
    node = ast.FunctionDef(
        name="test_func",
        args=ast.arguments(
            posonlyargs=[
                ast.arg(arg="a", annotation=ast.Name(id="int", ctx=ast.Load())),
                ast.arg(arg="b", annotation=ast.Name(id="str", ctx=ast.Load())),
            ],
            args=[],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body=[],
        decorator_list=[],
        returns=None,
    )

    # Test the function
    result = normalize_signature(node)
    assert result == "def test_func(a: int, b: str, /)"


def test_normalize_signature_with_kwonly_args():
    # Create a FunctionDef node with kwonly args
    node = ast.FunctionDef(
        name="test_func",
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            vararg=None,
            kwonlyargs=[
                ast.arg(arg="x", annotation=ast.Name(id="int", ctx=ast.Load())),
                ast.arg(arg="y", annotation=ast.Name(id="str", ctx=ast.Load())),
            ],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body=[],
        decorator_list=[],
        returns=None,
    )

    # Test the function
    result = normalize_signature(node)
    assert result == "def test_func(*, x: int, y: str)"


def test_normalize_signature_invalid_input():
    # Test with invalid input (not a FunctionDef or AsyncFunctionDef)
    node = ast.Expr(value=ast.Str(s="test"))

    # Test the function
    result = normalize_signature(node)
    assert result == ""
