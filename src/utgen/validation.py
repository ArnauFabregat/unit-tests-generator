import subprocess
import os
from utgen.logger import logger


def validate_individual_test(import_code: str, test_code: str) -> bool:
    """
    Validates a test by running it in a temporary file.

    Args:
        import_code (str): The import statements required for the test.
        test_code (str): The actual test case code to execute.

    Returns:
        bool: True if the test passes (exit code 0), False otherwise.
    """
    temp_filename = "temp_validation.py"
    full_code = f"{import_code}\n\n{test_code}"

    # Write the combined code to a temporary file
    with open(temp_filename, "w", encoding="utf-8", errors="replace") as f:
        f.write(full_code)

    # Execute pytest. 
    # -q: quiet mode
    # --tb=no: disable traceback to keep console clean
    result = subprocess.run(
        ["pytest", temp_filename, "-q", "--tb=no"], 
        capture_output=True
    )
    
    # Cleanup: remove the temporary file after execution
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
        
    return result.returncode == 0

def save_and_clean_tests(
    valid_tests: list[tuple[str, str]], 
    destination: str = "../tests/llm_generated_tests.py"
) -> None:
    """
    Aggregates valid tests, saves them to a file, and formats the output using Ruff.

    Args:
        valid_tests (List[Tuple[str, str]]): A list of tuples containing 
            (import_string, test_body_string).
        destination (str): The file path where the cleaned tests will be saved.
    """
    if not valid_tests:
        logger.debug("No valid tests available to save.")
        return

    # Ensure the directory exists
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    # 1. Separate into two blocks: all imports and all test bodies
    import_block: list[str] = []
    test_block: list[str] = []
    
    for imp, code in valid_tests:
        import_block.append(imp.strip())
        test_block.append(code.strip())
    
    # 2. Concatenate: First all imports, then all tests
    # We join with newlines to ensure clean separation
    final_content = "\n".join(import_block) + "\n\n" + "\n\n".join(test_block)

    with open(destination, "w", encoding="utf-8", errors="replace") as f:
        f.write(final_content)

    # 3. Use Ruff to organize and clean the generated file
    logger.debug(f"Cleaning {destination} with Ruff...")
    
    # Sort imports and remove duplicates (isort behavior)
    subprocess.run(["ruff", "check", "--select", "I", "--fix", destination], capture_output=True)
    
    # Remove unused variables/imports and fix common linting errors
    subprocess.run(["ruff", "check", "--fix", destination], capture_output=True)
    
    # Format code (Black-style formatting)
    subprocess.run(["ruff", "format", destination], capture_output=True)

    logger.debug(f"Process finished. File saved at: {destination}")
