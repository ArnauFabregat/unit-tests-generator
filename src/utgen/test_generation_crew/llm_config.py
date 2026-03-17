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

# --- OPENROUTER CONFIGURATION ---
# Unified API access to various open-source and proprietary models.
openrouter_llm = LLM(
    model=os.getenv("LLM_OPENROUTER_MODEL", ""),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("LLM_OPENROUTER_API_KEY"),
)
"""LLM: OpenRouter instance used as a gateway for diverse model selection."""
