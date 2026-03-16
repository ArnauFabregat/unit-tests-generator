import ast

from utgen.raggraph.parser import CodeGraphBuilder2


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


def test_attach_parents_with_nested_ast():
    """
    Test attach_parents with a nested AST containing multiple levels.
    """
    # Arrange
    fn_node = ast.FunctionDef(
        name="outer_function",
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[
            ast.FunctionDef(
                name="inner_function",
                args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
                body=[],
                decorator_list=[],
                returns=None,
                type_comment=None,
            )
        ],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    # Act
    CodeGraphBuilder2.attach_parents(fn_node)

    # Assert
    # Verify that the outer function has no parent (it's the root)
    assert not hasattr(fn_node, "parent")

    # Verify that the inner function has the outer function as parent
    inner_fn = fn_node.body[0]
    assert hasattr(inner_fn, "parent")
    assert inner_fn.parent is fn_node


def test_attach_parents_with_module_ast():
    """
    Test attach_parents with a module-level AST containing multiple functions.
    """
    # Arrange
    module = ast.parse("""

def func1():
    pass

def func2():
    pass
    """)

    # Act
    CodeGraphBuilder2.attach_parents(module)

    # Assert
    # Verify that the module has no parent (it's the root)
    assert not hasattr(module, "parent")

    # Verify that both functions have the module as parent
    func1, func2 = module.body
    assert hasattr(func1, "parent")
    assert func1.parent is module
    assert hasattr(func2, "parent")
    assert func2.parent is module


def test_attach_parents_with_class_ast():
    """
    Test attach_parents with a class definition AST.
    """
    # Arrange
    class_node = ast.ClassDef(
        name="MyClass",
        bases=[],
        keywords=[],
        body=[
            ast.FunctionDef(
                name="method",
                args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
                body=[],
                decorator_list=[],
                returns=None,
                type_comment=None,
            )
        ],
        decorator_list=[],
        docstring=None,
    )

    # Act
    CodeGraphBuilder2.attach_parents(class_node)

    # Assert
    # Verify that the class has no parent (it's the root)
    assert not hasattr(class_node, "parent")

    # Verify that the method has the class as parent
    method = class_node.body[0]
    assert hasattr(method, "parent")
    assert method.parent is class_node


def test_attach_parents_with_if_statement():
    """
    Test attach_parents with an if statement AST.
    """
    # Arrange
    if_node = ast.If(
        test=ast.Name(id="condition", ctx=ast.Load()),
        body=[ast.Expr(value=ast.Constant(value="true"))],
        orelse=[ast.Expr(value=ast.Constant(value="false"))],
        type_comment=None,
    )

    # Act
    CodeGraphBuilder2.attach_parents(if_node)

    # Assert
    # Verify that the if statement has no parent (it's the root)
    assert not hasattr(if_node, "parent")

    # Verify that the body and orelse nodes have the if statement as parent
    true_expr, false_expr = if_node.body[0], if_node.orelse[0]
    assert hasattr(true_expr, "parent")
    assert true_expr.parent is if_node
    assert hasattr(false_expr, "parent")
    assert false_expr.parent is if_node


def test_attach_parents_with_for_loop():
    """
    Test attach_parents with a for loop AST.
    """
    # Arrange
    for_node = ast.For(
        target=ast.Name(id="item", ctx=ast.Store()),
        iter=ast.Call(func=ast.Name(id="range", ctx=ast.Load()), args=[ast.Constant(value=10)], keywords=[]),
        body=[
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="print", ctx=ast.Load()), args=[ast.Name(id="item", ctx=ast.Load())], keywords=[]
                )
            )
        ],
        orelse=[],
        type_comment=None,
    )

    # Act
    CodeGraphBuilder2.attach_parents(for_node)

    # Assert
    # Verify that the for loop has no parent (it's the root)
    assert not hasattr(for_node, "parent")

    # Verify that the body nodes have the for loop as parent
    print_call = for_node.body[0]
    assert hasattr(print_call, "parent")
    assert print_call.parent is for_node


def test_attach_parents_with_try_except():
    """
    Test attach_parents with a try-except AST.
    """
    # Arrange
    try_node = ast.Try(
        body=[ast.Expr(value=ast.Call(func=ast.Name(id="dangerous_function", ctx=ast.Load()), args=[], keywords=[]))],
        handlers=[
            ast.ExceptHandler(
                type=ast.Name(id="Exception", ctx=ast.Load()),
                name=None,
                body=[
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Name(id="print", ctx=ast.Load()),
                            args=[ast.Constant(value="Error occurred")],
                            keywords=[],
                        )
                    )
                ],
            )
        ],
        orelse=[],
        finalbody=[ast.Expr(value=ast.Call(func=ast.Name(id="cleanup", ctx=ast.Load()), args=[], keywords=[]))],
        type_comment=None,
    )

    # Act
    CodeGraphBuilder2.attach_parents(try_node)

    # Assert
    # Verify that the try statement has no parent (it's the root)
    assert not hasattr(try_node, "parent")

    # Verify that the body nodes have the try statement as parent
    dangerous_call = try_node.body[0]
    print_call = try_node.handlers[0].body[0]
    cleanup_call = try_node.finalbody[0]

    assert hasattr(dangerous_call, "parent")
    assert dangerous_call.parent is try_node
    assert hasattr(print_call, "parent")
    assert print_call.parent is try_node.handlers[0]
    assert hasattr(cleanup_call, "parent")
    assert cleanup_call.parent is try_node
