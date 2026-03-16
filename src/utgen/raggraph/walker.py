import ast
import os
from pathlib import Path
from typing import Generator
import networkx as nx

from utgen.raggraph.parser import CodeGraphBuilder1, CodeGraphBuilder2


def iter_python_files(path: str, skip_init: bool = True) -> Generator[str, None, None]:
    """
    Iterates over all .py files within a given directory path.

    Args:
        path (str): The root directory to start walking from.
        skip_init (bool): If True, ignores all '__init__.py' files. Defaults to True.

    Yields:
        Generator[str, None, None]: A generator yielding the POSIX path strings 
            of the Python files found.
    """
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                if skip_init and f == "__init__.py":
                    continue
                yield Path(root, f).as_posix()


def build_graph_from_directory(
    code_path: str, 
    skip_init: bool = True, 
    save_graph: bool = False, 
    save_path: str = ""
) -> nx.DiGraph:
    """
    Analyzes a directory and builds a directed graph representing the code structure.

    The process uses two passes:
    1. First pass (CodeGraphBuilder1) identifies nodes and basic structures.
    2. Second pass (CodeGraphBuilder2) attaches parent relationships and 
       detailed connections.

    Args:
        code_path (str): The root path of the source code to analyze.
        skip_init (bool): Whether to ignore package initialization files. Defaults to True.
        save_graph (bool): If True, exports the resulting graph to a GraphML file. 
            Defaults to False.
        save_path (str): The file path where the GraphML will be saved if save_graph 
            is True.

    Returns:
        nx.DiGraph: A NetworkX directed graph containing the code's structural 
            and relationship data.
    """
    graph = nx.DiGraph()

    # Pass 1: Node discovery and basic structure
    for file_path in iter_python_files(code_path, skip_init=skip_init):
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read())
        builder = CodeGraphBuilder1(code_path, file_path, graph)
        builder.visit(tree)

    # Pass 2: Contextualizing relationships and parent attachment
    for file_path in iter_python_files(code_path, skip_init=skip_init):
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read())
        builder = CodeGraphBuilder2(code_path, file_path, graph)
        builder.attach_parents(tree)
        builder.visit(tree)

    if save_graph and save_path:
        # To open with Gephi or other graph visualization tools
        nx.write_graphml(graph, save_path)

    return graph
