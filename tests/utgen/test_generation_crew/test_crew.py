from unittest.mock import Mock, patch

from utgen.test_generation_crew.crew import GUARDRAIL_MAX_RETRIES, TestGenerationCrew  # type: ignore


def test_init_defaults():
    """Test TestGenerationCrew initialization with default values."""
    mock_llm = Mock()
    crew = TestGenerationCrew(llm=mock_llm)
    assert crew._llm is mock_llm
    assert crew._guardrail_max_retries == GUARDRAIL_MAX_RETRIES
    assert crew._verbose is False


def test_init_explicit():
    """Test TestGenerationCrew initialization with explicit values."""
    mock_llm = Mock()
    crew = TestGenerationCrew(llm=mock_llm, guardrail_max_retries=10, verbose=True)
    assert crew._llm is mock_llm
    assert crew._guardrail_max_retries == 10
    assert crew._verbose is True


def test_test_generator_agent_returns_agent():
    """Test that test_generator_agent returns an Agent instance with correct config."""
    # Arrange
    mock_llm = Mock()
    crew = TestGenerationCrew(llm=mock_llm)
    # Set agents_config to mimic loaded YAML config
    crew.agents_config = {
        "test_generator_agent": {
            "role": "Test Generator",
            "goal": "Generate unit tests",
            "backstory": "Expert in testing",
        }
    }

    # Act
    with patch("utgen.test_generation_crew.crew.Agent") as MockAgent:
        agent = crew.test_generator_agent()

        # Assert
        MockAgent.assert_called_once()
        call_args, call_kwargs = MockAgent.call_args
        assert call_kwargs["config"] == {
            "role": "Test Generator",
            "goal": "Generate unit tests",
            "backstory": "Expert in testing",
        }
        assert call_kwargs["llm"] is mock_llm
        assert agent is MockAgent.return_value


def test_generate_unit_tests_task_returns_task():
    """Test generate_unit_tests_task returns a Task with correct configuration."""
    # Arrange
    mock_llm = Mock()
    crew = TestGenerationCrew(llm=mock_llm)
    # Set up required config attributes
    crew.tasks_config = {
        "generate_unit_tests_task": {
            "description": "Generate unit tests for {graph_context}",
            "expected_output": "JSON with test cases",
        }
    }
    crew.agents_config = {
        "test_generator_agent": {
            "role": "Test Generator",
            "goal": "Generate unit tests",
            "backstory": "Expert in testing",
        }
    }
    # Mock the agent method to return a known agent
    mock_agent = Mock()
    crew.test_generator_agent = Mock(return_value=mock_agent)

    # Act
    with patch("utgen.test_generation_crew.crew.Task") as MockTask:
        task = crew.generate_unit_tests_task()

        # Assert
        MockTask.assert_called_once()
        call_args, call_kwargs = MockTask.call_args
        assert call_kwargs["description"] == "Generate unit tests for {graph_context}"
        assert call_kwargs["expected_output"] == "JSON with test cases"
        assert call_kwargs["agent"] is mock_agent
        # Check guardrail is the expected function
        from utgen.test_generation_crew.guardrails import validate_tests_schema

        assert call_kwargs["guardrail"] is validate_tests_schema
        assert call_kwargs["guardrail_max_retries"] == crew._guardrail_max_retries
        assert task is MockTask.return_value
