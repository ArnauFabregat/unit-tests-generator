# type: ignore
"""
Test Generator Crew Orchestrator.

This module defines the TestGenerationCrew, which uses CrewAI's declarative
syntax to create a crew responsible for generating unit tests based on the
context provided from the RAG-Graph. The crew consists of a single agent that
generates unit tests for functions and methods identified in the source code.
"""

from crewai import Agent, Crew, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from utgen.constants import GUARDRAIL_MAX_RETRIES
from utgen.test_generation_crew.guardrails import validate_tests_schema


@CrewBase
class TestGenerationCrew:
    """
    Orchestrates the test generation process.

    This crew consists of a single agent responsible for generating unit tests based
    on the context provided from the RAG-Graph.

    Attributes:
        agents_config (str): Path to the YAML file defining agent personalities.
        tasks_config (str): Path to the YAML file defining task requirements.
        _llm (LLM): An instance of the language model to be used by the agents.
        _guardrail_max_retries (int): The number of times the agent is allowed
            to self-correct if the guardrail validation fails.
        _verbose (bool): Whether to output execution logs to the console.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(
        self,
        llm: LLM,
        guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
        verbose: bool = False,
    ) -> None:
        """
        Initializes the TestGenerationCrew with runtime configurations.

        Args:
            llm (LLM): An instance of a language model to be used by the agents.
            guardrail_max_retries (int): Maximum attempts for the guardrail loop.
            verbose (bool): Enable or disable detailed logging.
        """
        self._llm = llm
        self._guardrail_max_retries = guardrail_max_retries
        self._verbose = verbose

    @agent
    def test_generator_agent(self) -> Agent:
        """
        Defines the unit test generator Agent.

        The agent's role and goal are pulled from the agents_config YAML.

        Returns:
            Agent: A CrewAI Agent instance powered by OpenRouter.
        """
        return Agent(
            config=self.agents_config["test_generator_agent"],
            llm=self._llm,
        )

    @task
    def generate_unit_tests_task(self) -> Task:
        """
        Defines the unit tests generation task.

        This task includes a custom guardrail that validates the structure and
        content of the generated tests against a predefined schema. If the validation fails,
        the agent will be prompted to revise its output, with a maximum number of
        retries defined by _guardrail_max_retries.

        Returns:
            Task: A CrewAI Task instance with integrated validation logic.
        """
        task_config = self.tasks_config["generate_unit_tests_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.test_generator_agent(),
            guardrail=validate_tests_schema,
            guardrail_max_retries=self._guardrail_max_retries,
        )

    @crew
    def crew(self) -> Crew:
        """
        Assembles the test generation crew.

        Returns:
            Crew: A CrewAI Crew instance ready to execute the test generation task.
        """
        return Crew(
            name="Test generation crew",
            agents=self.agents,
            tasks=self.tasks,
            verbose=self._verbose,
            share_crew=self._verbose,
        )
