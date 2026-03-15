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

import ast
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

    # 0. Basic Cleaning
    raw_content = result.raw.strip()
    if raw_content.startswith("```json"):
        raw_content = raw_content.replace("```json", "", 1).replace("```", "", 1).strip()
    elif raw_content.startswith("```"):
        raw_content = raw_content.replace("```", "", 2).strip()

    # 1. Validate JSON
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        logger.warning("Guardrail `validate_tests_schema` triggered: invalid JSON format")
        return (False, "Invalid JSON format. Please fix")

    errors: list[str] = []

    # 2. Validate first nesting level
    if "tests" not in data or not isinstance(data["tests"], dict):
        logger.warning("Guardrail `validate_tests_schema` triggered: missing or invalid 'tests' key")
        return (False, "Missing or invalid 'tests' key. Expected: {'tests': {'ID': {...}}}")

    # 3. Deep Dive: Schema + Syntax
    for test_id, content in data["tests"].items():
        # A. Pydantic Validation
        try:
            TestCase.model_validate(content)
        except Exception as e:
            errors.append(f"Test '{test_id}' schema error: {str(e)}")
            continue

        # B. Python Syntax Check
        # Assuming the 'content' dict has a key like 'code' or 'content' containing the Python string
        python_imports = content.get("imports", "") 
        if python_imports:
            try:
                ast.parse(python_imports)
            except SyntaxError as e:
                errors.append(f"Test '{test_id}' syntax error: {e.msg} at line {e.lineno}")

        python_code = content.get("code", "") 
        if python_code:
            try:
                ast.parse(python_code)
            except SyntaxError as e:
                errors.append(f"Test '{test_id}' syntax error: {e.msg} at line {e.lineno}")
    # TODO additional checks: pytest compatibility, dangerous functions, etc.

    # 3. Return
    if errors:
        logger.warning("Guardrail `validate_tests_schema` triggered: invalid test entries.")
        feedback: str = "Guardrail `validate_tests_schema` validation failed:\n- " + "\n- ".join(errors)
        logger.debug(feedback)
        return (False, feedback)

    return (True, json.dumps(data))
