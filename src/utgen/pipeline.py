import json
from collections import defaultdict
from pathlib import Path

from crewai import LLM
from tqdm import tqdm

from utgen.logger import logger
from utgen.raggraph.utils import get_node_context
from utgen.raggraph.walker import build_graph_from_directory
from utgen.test_generation_crew.crew import TestGenerationCrew  # type: ignore
from utgen.validation import save_and_clean_tests, validate_individual_test


def pipeline(
    source_code_dir: str,
    tests_output_dir: str,
    llm: LLM,
    save_graph_path: str = "",
    overwrite: bool = False,
) -> None:
    """
    Main function to orchestrate the test generation process.
    Args:
        source_code_dir (str): Directory containing the source code to analyze.
        tests_output_dir (str): Directory where generated tests will be saved.
        llm (LLM): An instance of a language model to be used by the test generation crew.
        save_graph_path (str): Path to save the graph representation.
        overwrite (bool): If False, skip generation for files that already have a test file.
    """
    logger.info("Creating graph from source code...")
    g = build_graph_from_directory(code_path=source_code_dir, save_graph_path=save_graph_path)
    logger.info(f"Graph built with {g.number_of_nodes()} nodes and {g.number_of_edges()} edges.")

    logger.info("Started test generation process...")
    tests_results: defaultdict[str, dict[str, dict]] = defaultdict(dict)
    test_generator = TestGenerationCrew(llm=llm, guardrail_max_retries=5, verbose=False)

    for node_id, data in list(g.nodes(data=True)):
        if data["type"] in ["function", "method"]:
            p = Path(data["file"])
            new_filename = f"test_{p.stem}{p.suffix}"
            target_test_file = Path(tests_output_dir) / p.parent / new_filename

            if not overwrite and target_test_file.exists():
                logger.info(f"Skipping {node_id}: Test file already exists at {target_test_file}")
                continue

            logger.info(f"Generating tests for node: {node_id}")
            try:
                context = get_node_context(g=g, node_id=node_id)
                inputs = {"graph_context": context}

                response = test_generator.crew().kickoff(inputs=inputs)
                response_dict = json.loads(response.raw)

                # Store results using the relative path as key
                save_path = (p.parent / new_filename).as_posix()
                tests_results[save_path][node_id] = response_dict["tests"]

            except Exception:
                logger.error(f"Failed to generate tests for {node_id}.")
                continue
    logger.info("Test generation process completed.")

    logger.info("Validating and saving generated tests...")
    pbar = tqdm(tests_results.items(), desc="Overall Progress", unit="file")

    for save_path, nodes in pbar:
        accepted_tests: list[tuple[str, str]] = []

        for node_id, tests in nodes.items():
            base_import = (
                "from "
                + node_id.split("::")[0][:-3].replace("/", ".")
                + " import "
                + node_id.split("::")[-1].split(".")[0]
            )
            for name, values in tests.items():
                imports, code = values["imports"], values["code"]

                if base_import not in imports:
                    logger.debug(f"Added missing import `{base_import}` for test `{name}`.")
                    imports.append(base_import)

                imports = "\n".join(imports)

                if validate_individual_test(import_code=imports, test_code=code):
                    logger.debug(f"Test `{name}` accepted during validation.")
                    accepted_tests.append((imports, code))
                else:
                    logger.debug(f"Test `{name}` rejected during validation.")

        logger.debug(f"Saving cleaned tests for `{save_path}`...")
        save_and_clean_tests(valid_tests=accepted_tests, destination=f"{tests_output_dir}/{save_path}")
    logger.info("All tests validated and saved successfully.")
