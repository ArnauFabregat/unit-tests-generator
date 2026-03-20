import os


def pytest_configure(config):
    """
    This hook runs BEFORE any tests or modules are imported.
    """
    os.environ["LLM_OPENROUTER_MODEL"] = "openrouter/openrouter/el-meu-llm"
    os.environ["LLM_OPENROUTER_API_KEY"] = "sk-or-v1-fake-key-for-testing"
