from crewai import LLM
import json
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
    overwrite: Annotated[bool, typer.Option("--overwrite", "-o", help="Overwrite existing test files")] = False,
    model: Annotated[str, typer.Option("--model", "-m")] = "openai/gpt-4o",
    base_url: Annotated[str | None, typer.Option("--base-url", help="Base URL for LLM API")] = None,
    temperature: Annotated[float, typer.Option("--temperature")] = 0.3,
    max_tokens: Annotated[int, typer.Option("--max-tokens")] = 4096,
    llm_extra: Annotated[str | None, typer.Option("--llm-extra", help="JSON string of extra LLM params")] = None,
) -> None:
    """
    Generate unit tests based on your source code and RAG-Graph.
    """
    extra = json.loads(llm_extra) if llm_extra else {}
    llm = LLM(
        model=model,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        **extra,
    )
    logger.info("Initializing utgen...")
    logger.info(f"Source: {src_path} | Tests: {test_path} | Graph: {graph_path} | Overwrite: {overwrite}")

    pipeline(
        source_code_dir=str(src_path),
        tests_output_dir=str(test_path),
        save_graph_path=str(graph_path) if graph_path else "",
        overwrite=overwrite,
        llm=llm,
    )

    logger.info("Running coverage report...")
    try:
        subprocess.run(["pytest", str(test_path), f"--cov={src_path}", "--cov-report=term-missing"], check=True)
    except subprocess.CalledProcessError:
        logger.warning("Some tests failed or coverage couldn't be calculated.")
    except FileNotFoundError:
        logger.error("`pytest` not found. Make sure it's installed in your environment.")


if __name__ == "__main__":
    app()
