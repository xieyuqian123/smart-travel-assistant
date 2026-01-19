"""Configuration settings for the travel assistant."""

import os
from typing import Any, Optional

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm(structured_output: Optional[Any] = None, model_key: str = "PLANNER", model_name: Optional[str] = None) -> ChatOpenAI | Any:
    """Get the configured LLM instance.

    Args:
        structured_output: Optional schema to enforce structured output.
        model_key: Key suffix for model configuration (e.g., "PLANNER" or "TOOL").
                   Looks for env vars like MODEL_NAME_PLANNER or MODEL_NAME_TOOL.
                   Defaults to "PLANNER".
        model_name: Explicit model name to use. Overrides env vars.

    Returns:
        Configured ChatOpenAI instance (or structured output runnable).
    """
    # Default to generic MODEL_NAME if specific key not found
    if not model_name:
        default_model = os.getenv("MODEL_NAME", "gpt-4o")
        model_name = os.getenv(f"MODEL_NAME_{model_key}", default_model)
    
    # Allow overriding API key/base per model if needed, but usually shared
    api_key = os.getenv(f"OPENAI_API_KEY_{model_key}") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv(f"OPENAI_API_BASE_{model_key}") or os.getenv("OPENAI_API_BASE")
    
    temperature = float(os.getenv(f"TEMPERATURE_{model_key}", os.getenv("TEMPERATURE", "0.6")))

    if not api_key:
        # We might want to raise an error or just warn, but letting LangChain handle it is usually fine
        pass

    llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
        base_url=base_url,
        max_tokens=16384,  # Increase max tokens for detailed itineraries
    )

    if structured_output:
        return llm.with_structured_output(structured_output)
    
    return llm
