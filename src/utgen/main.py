import json
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from crewai import LLM

from utgen.logger import logger
from utgen.pipeline import pipeline

app = typer.Typer(help="UTGen: Unit test generation with RAG-Graph and LLMs")


@app.callback(invoke_without_command=True)
def run(
    src_path: Annotated[Path, typer.Option("--src_path", "-s", help="Path to source")],
    test_path: Annotated[Path, typer.Option("--test_path", "-t", help="Path to tests")],
    graph_path: Annotated[Path | None, typer.Option("--graph_path", "-g", help="Path to Graph")] = None,
    overwrite: Annotated[bool, typer.Option("--overwrite", "-o", help="Overwrite existing test files")] = False,
    model: Annotated[str, typer.Option("--model", "-m")] = "openai/gpt-4o",
    temperature: Annotated[float, typer.Option("--temperature")] = 0.3,
    max_tokens: Annotated[int, typer.Option("--max-tokens")] = 4096,
    base_url: Annotated[str | None, typer.Option("--base-url", help="Base URL for LLM API")] = None,
    llm_extra: Annotated[str | None, typer.Option("--llm-extra", help="JSON string of extra LLM params")] = None,
) -> None:
    """
    Generate unit tests based on your source code using a RAG-Graph approach.

    This command orchestrates the end-to-end pipeline: it parses the source code,
    optionally builds/exports a dependency graph, uses an LLM to generate
    comprehensive unit tests, and finally runs a coverage report via pytest.

    Args:
        src_path (Path): The filesystem path to the directory containing source code.
        test_path (Path): The filesystem path where generated tests will be saved.
        graph_path (Path | None): Optional path to export the RAG-Graph JSON.
        overwrite (bool): Whether to replace existing test files. Defaults to False.
        model (str): LLM identifier (e.g., 'openai/gpt-4o').
        temperature (float): Sampling randomness (0.0 to 1.0).
        max_tokens (int): Maximum token limit for the LLM response.
        base_url (str | None): Custom API endpoint for the LLM provider.
        llm_extra (str | None): JSON string containing additional LLM parameters.

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If the pytest execution fails.
        FileNotFoundError: If the pytest executable is not found in the environment.
        json.JSONDecodeError: If `llm_extra` is provided but is not valid JSON.
    """
    # Parse extra LLM parameters if provided
    extra = json.loads(llm_extra) if llm_extra else {}

    # Initialize the CrewAI LLM wrapper
    llm = LLM(
        model=model,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        **extra,
    )

    logger.info("Initializing utgen...")
    logger.info(f"Source: {src_path} | Tests: {test_path} | Graph: {graph_path} | Overwrite: {overwrite}")

    # Execute the core logic
    pipeline(
        source_code_dir=str(src_path),
        tests_output_dir=str(test_path),
        save_graph_path=str(graph_path) if graph_path else "",
        overwrite=overwrite,
        llm=llm,
    )

    # Post-generation: Run tests and report coverage
    logger.info("Running coverage report...")
    try:
        subprocess.run(["pytest", str(test_path), f"--cov={src_path}", "--cov-report=term-missing"], check=True)
    except subprocess.CalledProcessError:
        logger.warning("Some tests failed or coverage couldn't be calculated.")
    except FileNotFoundError:
        logger.error("`pytest` not found. Make sure it's installed in your environment.")


if __name__ == "__main__":
    app()
