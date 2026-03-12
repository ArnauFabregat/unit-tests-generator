# type: ignore
"""
Test Generator Crew Orchestrator.

This module defines the TestGenerationCrew, which uses CrewAI's declarative
syntax to ...
"""

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

from utgen.constants import GUARDRAIL_MAX_RETRIES
from utgen.test_generation_crew.llm_config import openrouter_llm


from pydantic import BaseModel

class TestOutput(BaseModel):
    code: str


@CrewBase
class TestGenerationCrew:
    """
    Orchestrates the test generation process.

    This crew consists of ...

    Attributes:
        agents_config (str): Path to the YAML file defining agent personalities.
        tasks_config (str): Path to the YAML file defining task requirements.
        _guardrail_max_retries (int): The number of times the agent is allowed
            to self-correct if the guardrail validation fails.
        _verbose (bool): Whether to output execution logs to the console.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(
        self,
        guardrail_max_retries: int = GUARDRAIL_MAX_RETRIES,
        verbose: bool = False,
    ) -> None:
        """
        Initializes the TestGenerationCrew with runtime configurations.

        Args:
            guardrail_max_retries (int): Maximum attempts for the guardrail loop.
            verbose (bool): Enable or disable detailed logging.
        """
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
            llm=openrouter_llm,
        )

    @task
    def generate_unit_tests_task(self) -> Task:
        """
        Defines the unit tests generation task.

        This task includes a custom guardrail ...

        Returns:
            Task: A CrewAI Task instance with integrated validation logic.
        """
        task_config = self.tasks_config["generate_unit_tests_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.test_generator_agent(),
            # output_json=TestOutput,
            # guardrail=validate_classifier_output,
            # guardrail_max_retries=self._guardrail_max_retries,
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
            agents=[self.test_generator_agent()],
            tasks=[self.generate_unit_tests_task()],
            verbose=self._verbose,
        )
