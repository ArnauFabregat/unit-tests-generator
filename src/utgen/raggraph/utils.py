import ast
import textwrap
from typing import Any

import networkx as nx


def get_node_context(g: nx.DiGraph, node_id: str) -> str:
    """
    Generates a comprehensive text context for a specific node in the code graph.

    This includes the node's source code, its relationships (incoming/outgoing
    edges), and detailed information about its immediate neighbors.

    Args:
        g (nx.DiGraph): The NetworkX directed graph containing the code structure.
        node_id (str): The unique identifier of the node (file::type::name).

    Returns:
        str: A formatted string block ready to be used as LLM context.
    """
    context: str = ""

    # 1. Node Attributes
    node_data = g.nodes[node_id]
    context += "### NODE INFO ###\n"
    context += f"file::type::name -> {node_id}\n\n"

    src = node_data.get("source") or ""
    context += "source:\n" + src + "\n\n"

    # 2. Outgoing edges (what this node calls or depends on)
    out_edges: list[str] = []
    for _, dst, data in g.out_edges(node_id, data=True):
        if g.nodes[dst].get("type") == "nested_function":
            continue
        rel = data.get("rel")
        out_edges.append(f"{node_id} -[{rel}]-> {dst}")

    if out_edges:
        context += "### OUTGOING EDGES ###\n"
        context += "\n".join(out_edges) + "\n\n"

    # 3. Incoming edges (what calls or uses this node)
    in_edges: list[str] = []
    for src_id, _, data in g.in_edges(node_id, data=True):
        if g.nodes[src_id].get("type") == "nested_function":
            continue
        rel = data.get("rel")
        in_edges.append(f"{src_id} -[{rel}]-> {node_id}")

    if in_edges:
        context += "### INCOMING EDGES ###\n"
        context += "\n".join(in_edges) + "\n\n"

    # 4. Neighbor context (providing deeper details on related nodes)
    neighbor_ids: set[str] = set()

    # nodes referenced by outgoing edges
    for _, dst in g.out_edges(node_id):
        if g.nodes[dst].get("type") not in ["file", "nested_function"]:
            neighbor_ids.add(dst)

    # nodes referencing this node
    for src_id, _ in g.in_edges(node_id):
        if g.nodes[src_id].get("type") not in ["file", "nested_function"]:
            neighbor_ids.add(src_id)

    neighbor_blocks: list[str] = []
    for nid in neighbor_ids:
        nd = g.nodes[nid]
        blk = "--- Neighbor Node ---\n"
        blk += f"file::type::name -> {nid}\n"
        blk += f"signature: {nd.get('signature')}\n"
        blk += "docstring:\n" + (nd.get("docstring") or "") + "\n"
        neighbor_blocks.append(blk)

    if neighbor_blocks:
        context += "### NEIGHBOR NODE DETAILS ###\n"
        context += "".join(neighbor_blocks)

    return context


def get_source_segment(file_path: str, node: ast.AST) -> str:
    """
    Extracts the raw source code segment for a specific AST node from a file.

    Args:
        file_path (str): Path to the .py file.
        node (ast.AST): The AST node to extract.

    Returns:
        str: The extracted source code string, or an empty string if failed.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            src = f.read()
    except OSError:
        return ""

    # Preferred: use built-in ast tool if available
    try:
        seg = ast.get_source_segment(src, node)
        if seg is not None:
            return seg
    except Exception:
        pass

    # Fallback: manual line slicing
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        lines = src.splitlines()
        # AST line numbers are 1-based
        snippet = "\n".join(lines[node.lineno - 1 : node.end_lineno])
        return textwrap.dedent(snippet)

    return ""


def canonical_id(*parts: str) -> str:
    """
    Creates a standardized string identifier for graph nodes.

    Args:
        *parts (str): String components like filename, type, and name.

    Returns:
        str: A joined string using '::' as a separator.
    """
    return "::".join(parts)


def normalize_signature(node: ast.AST) -> str:
    """
    Reconstructs a valid Python function signature from an AST node.

    This includes arguments, type hints, and return annotations.

    Args:
        node (ast.AST): The AST function definition node.

    Returns:
        str: A string representing the 'def function_name(...):' signature.
    """
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""

    def unparse(x: Any) -> str:
        try:
            return ast.unparse(x)
        except Exception:
            return ""

    parts: list[str] = []

    # Positional-only args
    pos_only = getattr(node.args, "posonlyargs", [])
    for a in pos_only:
        s = a.arg
        if a.annotation:
            s += f": {unparse(a.annotation)}"
        parts.append(s)
    if pos_only:
        parts.append("/")

    # Standard args
    for a in node.args.args:
        s = a.arg
        if a.annotation:
            s += f": {unparse(a.annotation)}"
        parts.append(s)

    # *args
    if node.args.vararg:
        s = "*" + node.args.vararg.arg
        if node.args.vararg.annotation:
            s += f": {unparse(node.args.vararg.annotation)}"
        parts.append(s)
    elif node.args.kwonlyargs:
        parts.append("*")

    # Keyword-only args
    for a in node.args.kwonlyargs:
        s = a.arg
        if a.annotation:
            s += f": {unparse(a.annotation)}"
        parts.append(s)

    # **kwargs
    if node.args.kwarg:
        s = "**" + node.args.kwarg.arg
        if node.args.kwarg.annotation:
            s += f": {unparse(node.args.kwarg.annotation)}"
        parts.append(s)

    ret = ""
    if node.returns:
        ret = f" -> {unparse(node.returns)}"

    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({', '.join(parts)}){ret}"
