import pytest

from utgen.test_generation_crew.crew import TestGenerationCrew


def test_generate_unit_tests_task_with_missing_config():
    """
    Test generate_unit_tests_task when generate_unit_tests_task config is missing.
    """
    # Arrange
    # Mock the tasks_config without the required key
    tasks_config = {"other_task": {"description": "Other task description"}}

    # Initialize the crew with mock config
    crew = TestGenerationCrew()
    crew.tasks_config = tasks_config

    # Act & Assert
    with pytest.raises(KeyError, match="generate_unit_tests_task"):
        crew.generate_unit_tests_task()
