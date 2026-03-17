import subprocess
from pathlib import Path
from typing import Annotated

import typer

from utgen.logger import logger
from utgen.pipeline import pipeline

app = typer.Typer(help="UTGen: Unit test generation with RAG-Graph and LLMs")


@app.callback(invoke_without_command=True)
def run(
    src_path: Annotated[Path, typer.Option("--src_path", "-s", help="Path to source")],
    test_path: Annotated[Path, typer.Option("--test_path", "-t", help="Path to tests")],
    graph_path: Annotated[Path | None, typer.Option("--graph_path", "-g", help="Path to Graph")] = None,
) -> None:
    """
    Generate unit tests based on your source code and RAG-Graph.
    """
    logger.info("Initializing utgen...")
    logger.info(f"Source: {src_path} | Tests: {test_path} | Graph: {graph_path}")

    pipeline(
        source_code_dir=str(src_path),
        tests_output_dir=str(test_path),
        save_graph_path=str(graph_path) if graph_path else "",
    )

    logger.info("Running coverage report...")
    # We run pytest-cov on the newly generated test directory
    # --cov points to the source code we want to measure
    try:
        subprocess.run(["pytest", str(test_path), f"--cov={src_path}", "--cov-report=term-missing"], check=True)
    except subprocess.CalledProcessError:
        logger.warning("Some tests failed or coverage couldn't be calculated.")
    except FileNotFoundError:
        logger.error("`pytest` not found. Make sure it's installed in your environment.")


if __name__ == "__main__":
    app()
