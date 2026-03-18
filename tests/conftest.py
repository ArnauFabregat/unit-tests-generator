import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """
    Configures the environment variables required for tests.
    This prevents ValueErrors and avoids real API calls during testing
    without needing extra libraries or .env files.
    """
    # Mock environment variables for LLM configuration
    os.environ["LLM_OPENROUTER_MODEL"] = "openrouter/openrouter/el-meu-llm"
    os.environ["LLM_OPENROUTER_API_KEY"] = "sk-or-v1-fake-key-for-testing"
