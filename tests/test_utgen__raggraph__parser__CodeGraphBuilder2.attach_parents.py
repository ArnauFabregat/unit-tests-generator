import ast

from utgen.raggraph.parser import CodeGraphBuilder2


def test_attach_parents_basic():
    # Create a simple AST tree
    module = ast.Module(body=[], type_ignores=[])
    func = ast.FunctionDef(name="foo", args=ast.arguments(), body=[], decorator_list=[], returns=None)
    module.body.append(func)

    # Call the method
    CodeGraphBuilder2.attach_parents(module)

    # Verify the parent relationship
    assert hasattr(func, "parent")
    assert func.parent == module


def test_attach_parents_nested():
    # Create a nested AST tree
    module = ast.Module(body=[], type_ignores=[])
    func = ast.FunctionDef(name="foo", args=ast.arguments(), body=[], decorator_list=[], returns=None)
    call = ast.Call(func=ast.Name(id="bar", ctx=ast.Load()), args=[], keywords=[])
    func.body.append(call)
    module.body.append(func)

    # Call the method
    CodeGraphBuilder2.attach_parents(module)

    # Verify the parent relationships
    assert hasattr(func, "parent")
    assert func.parent == module
    assert hasattr(call, "parent")
    assert call.parent == func


def test_attach_parents_no_children():
    # Create a simple AST node with no children
    node = ast.Name(id="x", ctx=ast.Load())

    # Call the method
    CodeGraphBuilder2.attach_parents(node)

    # Verify no parent attribute was added (no children to iterate)
    assert not hasattr(node, "parent")


def test_attach_parents_module_only():
    # Create a module with no body
    module = ast.Module(body=[], type_ignores=[])

    # Call the method
    CodeGraphBuilder2.attach_parents(module)

    # Verify no parent attributes were added (no children to iterate)
    assert not hasattr(module, "parent")
