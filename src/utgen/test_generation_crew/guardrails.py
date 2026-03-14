"""
Task Output Guardrails Module.

This module provides validation functions (guardrails) designed to verify that
AI agents return structured data matching the expected JSON schema. It
performs multi-level validation: JSON syntax, pydantic schema, python syntax for code snippets,
dangerous functions detection and pytest compatibility checks.

- Validar codi python amb try ast.parse(x) except Exception as e: fail("Codi no vàlid: " + str(e))
- Validar funcions perilloses: prohibits = ['os.remove', 'shutil.rmtree', 'subprocess.run', 'os.system']
- Validar compatibilitat amb pytest: if not v.strip().startswith("def test_")
"""

import json
from typing import Any

from crewai import TaskOutput

from utgen.test_generation_crew.schemas import TestCase
from utgen.logger import logger


def validate_tests_schema(result: TaskOutput) -> tuple[bool, Any]:
    """
    Validates the JSON format and schema for LLMTestOutput outputs.

    This guardrail ensures the LLM output follows a nested dictionary structure:
    {'tests': {'TEST_ID': TestCase}}. It uses Pydantic to provide
    detailed error feedback if technical validation fails.

    Parameters
    ----------
    result : TaskOutput
        The raw output object from the CrewAI task containing the generated string.

    Returns
    -------
    tuple[bool, Any]
        A tuple where the first element is a success flag (bool).
        The second element is either the cleaned JSON string (on success)
        or descriptive error feedback (on failure).
    """
    logger.debug(f"Guardrail input:\n{result.raw}")
    # Split into lines, slice from index 1 to -1, then rejoin
    lines = result.raw.splitlines()
    test_content = "\n".join(lines[1:-1])

    # 1. Validate JSON
    try:
        data = json.loads(test_content)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_tests_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    errors: list[str] = []

    # 1. Validate first nesting level
    if "tests" not in data or not isinstance(data["tests"], dict):
        logger.warning("Guardrail `validate_tests_schema` triggered: missing or invalid 'tests' key")
        return (False, "Missing or invalid 'tests' key. Expected: {'tests': {'ID': {...}}}")

    # 2. Deep Dive into each test entry
    for test_id, content in data["tests"].items():
        try:
            # Use Pydantic to validate the inner object
            # This checks types, missing fields, and extra fields in one go
            TestCase.model_validate(content)
        except Exception as e:
            # Pydantic's error messages are very descriptive for LLMs
            errors.append(f"Test '{test_id}' validation error: {str(e)}")

    # TODO additional checks: puython syntax, pytest compatibility, dangerous functions, etc.

    # 3. Return
    if errors:
        logger.warning("Guardrail `validate_tests_schema` triggered: invalid test entries.")
        feedback: str = "Guardrail `validate_tests_schema` validation failed:\n- " + "\n- ".join(errors)
        logger.debug(feedback)
        return (False, feedback)

    return (True, json.dumps(data))
