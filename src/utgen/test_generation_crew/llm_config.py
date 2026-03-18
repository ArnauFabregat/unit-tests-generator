"""
LLM Configurations Module.

This module initializes various Large Language Model (LLM) instances using the
CrewAI LLM wrapper. It centralizes model parameters (temperature, tokens, etc.)
and environment variable management for Groq, Gemini, and OpenRouter providers.
"""

import os

from crewai import LLM
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_required_env(key: str) -> str:
    """
    Retrieves an environment variable and validates its presence.

    Args:
        key (str): The name of the environment variable to retrieve.

    Returns:
        str: The value of the environment variable.

    Raises:
        ValueError: If the environment variable is not set or is an empty string.
    """
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


# --- OPENROUTER CONFIGURATION ---
# Unified API access to various open-source and proprietary models.
openrouter_llm = LLM(
    model=get_required_env("LLM_OPENROUTER_MODEL"),
    base_url="https://openrouter.ai/api/v1",
    api_key=get_required_env("LLM_OPENROUTER_API_KEY"),
    temperature=0.3,
)
"""LLM: OpenRouter instance used as a gateway for diverse model selection."""
