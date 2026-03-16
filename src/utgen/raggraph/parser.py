import os
import ast
from typing import Optional, Any
import networkx as nx

from utgen.raggraph.utils import get_source_segment, canonical_id, normalize_signature


class CodeGraphBuilder1(ast.NodeVisitor):
    """
    First pass of code analysis: Builds nodes and structural edges.
    
    This visitor creates nodes for files, classes, and functions/methods.
    It establishes 'defines' and 'has_method' relationships.
    """

    def __init__(self, code_path: str, file_path: str, graph: nx.DiGraph):
        """
        Initializes the first-pass builder.

        Args:
            code_path (str): The root directory of the project.
            file_path (str): The specific file being visited.
            graph (nx.DiGraph): The graph instance to populate.
        """
        self.file_path: str = file_path
        self.file_path_clean: str = file_path.removeprefix(f'{code_path}/')
        self.graph: nx.DiGraph = graph

        self.current_file_id: str = canonical_id(self.file_path_clean)
        self.current_class: Optional[str] = None
        self.function_stack: list[str] = []
        self.current_scope: Optional[str] = None

        # --- Create file node ---
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError:
            content = ""

        self.graph.add_node(
            self.current_file_id,
            type="file",
            name=os.path.basename(self.file_path_clean),
            file=self.file_path_clean,
            signature="None",
            docstring="None",
            source=content
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visits class definitions and adds class nodes and 'defines' edges."""
        class_id = canonical_id(self.file_path_clean, "class", node.name)

        self.graph.add_node(
            class_id,
            type="class",
            name=node.name,
            file=self.file_path_clean,
            signature=node.name or "None",
            docstring=ast.get_docstring(node) or "None",
            source=get_source_segment(self.file_path, node)
        )

        # The file defines the class
        self.graph.add_edge(self.current_file_id, class_id, rel="defines")

        prev_class = self.current_class
        self.current_class = class_id
        self.generic_visit(node)
        self.current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visits function/method definitions and adds corresponding nodes and edges."""
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

        fn_id = canonical_id(self.file_path_clean, parent_type, name)

        self.graph.add_node(
            fn_id,
            type=parent_type,
            name=name,
            file=self.file_path_clean,
            signature=normalize_signature(node) or "None",
            docstring=ast.get_docstring(node) or "None",
            source=get_source_segment(self.file_path, node)
        )

        # Parent relationship logic
        if is_method:
            self.graph.add_edge(self.current_class, fn_id, rel="has_method")
        elif is_nested:
            self.graph.add_edge(self.function_stack[-1], fn_id, rel="defines")
        else:
            self.graph.add_edge(self.current_file_id, fn_id, rel="defines")

        # Handle nesting scopes
        self.function_stack.append(fn_id)
        prev_scope = self.current_scope
        self.current_scope = fn_id
        self.generic_visit(node)
        self.current_scope = prev_scope
        self.function_stack.pop()


class CodeGraphBuilder2(ast.NodeVisitor):
    """
    Second pass of code analysis: Detects semantic relationships.
    
    This visitor finds 'calls' and 'references' by looking up symbols 
    in the previously built graph.
    """
    def __init__(self, code_path: str, file_path: str, graph: nx.DiGraph):
        """
        Initializes the second-pass builder.

        Args:
            code_path (str): The root directory of the project.
            file_path (str): The specific file being visited.
            graph (nx.DiGraph): The graph populated in Pass 1.
        """
        self.file_path: str = file_path
        self.file_path_clean: str = file_path.removeprefix(f'{code_path}/')
        self.graph: nx.DiGraph = graph

        self.current_file_id: str = canonical_id(self.file_path_clean)
        self.current_class: Optional[str] = None
        self.function_stack: list[str] = []
        self.current_scope: Optional[str] = None
        self.dst_canonical_id: Optional[str] = None

    @staticmethod
    def attach_parents(node: ast.AST) -> None:
        """
        Recursively attaches a 'parent' attribute to every node in the AST.
        
        Args:
            node (ast.AST): The root node of the tree to process.
        """
        for child in ast.iter_child_nodes(node):
            setattr(child, "parent", node)
            CodeGraphBuilder2.attach_parents(child)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Tracks current class scope for method identification."""
        class_id = canonical_id(self.file_path_clean, "class", node.name)
        prev = self.current_class
        self.current_class = class_id
        self.generic_visit(node)
        self.current_class = prev

    def visit_FunctionDef(self, node: Any) -> None:
        """Tracks current function scope to attribute calls and references."""
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

        fn_id = canonical_id(self.file_path_clean, parent_type, name)

        self.function_stack.append(fn_id)
        prev = self.current_scope
        self.current_scope = fn_id
        self.generic_visit(node)
        self.current_scope = prev
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Handles async functions same as regular functions."""
        return self.visit_FunctionDef(node)

    def is_local_symbol(self, name: str) -> bool:
        """
        Checks if a name refers to a symbol existing in the graph nodes.

        Args:
            name (str): The name of the symbol to look up.

        Returns:
            bool: True if found locally in the graph.
        """
        for nid, data in self.graph.nodes(data=True):
            if data.get("name") == name:
                self.dst_canonical_id = nid
                return True
        return False

    def visit_Name(self, node: ast.Name) -> None:
        """Analyzes variable names to detect calls or semantic references."""
        if not self.current_scope:
            return

        name = node.id
        parent = getattr(node, "parent", None)

        # Detect CALL (if the name is the function being called)
        if isinstance(parent, ast.Call) and parent.func is node:
            if self.is_local_symbol(name):
                self.graph.add_edge(self.current_scope, self.dst_canonical_id, rel="calls")
            return

        # Detect REFERENCE (usage without calling)
        if self.is_local_symbol(name):
            self.graph.add_edge(self.current_scope, self.dst_canonical_id, rel="references")

    def visit_Call(self, node: ast.Call) -> None:
        """Custom traversal for calls to ensure proper order of visitation."""
        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)
        for kw in node.keywords:
            if kw.value:
                self.visit(kw.value)
