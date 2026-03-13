# type: ignore
import os
import ast
from utgen.raggraph.utils import get_source_segment, canonical_id, normalize_signature


class CodeGraphBuilder1(ast.NodeVisitor):
    """
    First pass: build nodes for files, classes, functions/methods with metadata.
    Adds edges for: defines, has_method (class→method), and nested defines.
    """

    def __init__(self, file_path, graph):
        self.file_path = file_path
        self.graph = graph

        self.current_file_id = canonical_id(file_path)
        self.current_class = None
        self.function_stack = []
        self.current_scope = None

        # --- Create file node ---
        self.graph.add_node(
            self.current_file_id,
            type="file",
            name=os.path.basename(file_path),
            file=file_path,
            signature="None",
            docstring="None",
            source=open(file_path).read()
        )

    # ---------------------
    # Classes
    # ---------------------
    def visit_ClassDef(self, node):
        class_id = canonical_id(self.file_path, "class", node.name)

        self.graph.add_node(
            class_id,
            type="class",
            name=node.name,
            file=self.file_path,
            signature=node.name or "None",
            docstring=ast.get_docstring(node) or "None",
            source=get_source_segment(self.file_path, node)
        )

        # the file defines the class
        self.graph.add_edge(self.current_file_id, class_id, rel="defines")

        prev_class = self.current_class
        self.current_class = class_id
        self.generic_visit(node)
        self.current_class = prev_class

    # ---------------------
    # Functions / Methods
    # ---------------------
    def visit_FunctionDef(self, node):

        is_method = self.current_class is not None
        is_nested = len(self.function_stack) > 0 and not is_method

        # Generate a name
        if is_method:
            parent_type = "method"
            name = f"{self.current_class.split('::')[-1]}.{node.name}"
        elif is_nested:
            parent_type = "nested_function"
            name = f"{self.function_stack[-1].split('::')[-1]}.{node.name}"
        else:
            parent_type = "function"
            name = node.name

        fn_id = canonical_id(self.file_path, parent_type, name)

        # Create node
        self.graph.add_node(
            fn_id,
            type=parent_type,
            name=name,
            file=self.file_path,
            signature=normalize_signature(node) or "None",
            docstring=ast.get_docstring(node) or "None",
            source=get_source_segment(self.file_path, node)
        )

        # Parent relationship
        if is_method:
            self.graph.add_edge(self.current_class, fn_id, rel="has_method")
        elif is_nested:
            self.graph.add_edge(self.function_stack[-1], fn_id, rel="defines")
        else:
            self.graph.add_edge(self.current_file_id, fn_id, rel="defines")

        # --- nested function handling ---
        self.function_stack.append(fn_id)

        prev_scope = self.current_scope
        self.current_scope = fn_id
        self.generic_visit(node)
        self.current_scope = prev_scope

        self.function_stack.pop()


class CodeGraphBuilder2(ast.NodeVisitor):
    """
    Second pass: detect both calls and references.
    """
    def __init__(self, file_path, graph):
        self.file_path = file_path
        self.graph = graph

        self.current_file_id = canonical_id(file_path)
        self.current_class = None
        self.function_stack = []   # NEW
        self.current_scope = None
        self.dst_canonical_id = None

    @staticmethod
    def attach_parents(node: ast.AST):
        for child in ast.iter_child_nodes(node):
            setattr(child, "parent", node)
            CodeGraphBuilder2.attach_parents(child)

    # -------------------
    # Class
    # -------------------
    def visit_ClassDef(self, node):
        class_id = canonical_id(self.file_path, "class", node.name)
        prev = self.current_class
        self.current_class = class_id
        self.generic_visit(node)
        self.current_class = prev

    # -------------------
    # Functions / Methods
    # -------------------
    def visit_FunctionDef(self, node):

        is_method = self.current_class is not None
        is_nested = len(self.function_stack) > 0 and not is_method

        if is_method:
            parent_type = "method"
            name = f"{self.current_class.split('::')[-1]}.{node.name}"
        elif is_nested:
            parent_type = "nested_function"
            name = f"{self.function_stack[-1].split('::')[-1]}.{node.name}"
        else:
            parent_type = "function"
            name = node.name

        fn_id = canonical_id(self.file_path, parent_type, name)

        self.function_stack.append(fn_id)
        prev = self.current_scope
        self.current_scope = fn_id

        self.generic_visit(node)

        self.current_scope = prev
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    # -------------------
    # Symbol lookup
    # -------------------
    def is_local_symbol(self, name: str) -> bool:
        for nid, data in self.graph.nodes(data=True):
            if data.get("name") == name:
                self.dst_canonical_id = nid
                return True
        return False

    # -------------------
    # visit_Name: references & calls
    # -------------------
    def visit_Name(self, node):
        if not self.current_scope:
            return

        name = node.id
        parent = getattr(node, "parent", None)

        # CALL
        if isinstance(parent, ast.Call) and parent.func is node:
            if self.is_local_symbol(name):
                self.graph.add_edge(self.current_scope, self.dst_canonical_id, rel="calls")
            return

        # REFERENCE
        if self.is_local_symbol(name):
            self.graph.add_edge(self.current_scope, self.dst_canonical_id, rel="references")

    # -------------------
    # visit_Call – only traversal
    # -------------------
    def visit_Call(self, node):
        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)
        for kw in node.keywords:
            if kw.value:
                self.visit(kw.value)
