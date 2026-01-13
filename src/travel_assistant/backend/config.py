"""Configuration settings for the travel assistant."""

import os
from typing import Any, Optional

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm(structured_output: Optional[Any] = None) -> ChatOpenAI | Any:
    """Get the configured LLM instance.

    Args:
        structured_output: Optional schema to enforce structured output.

    Returns:
        Configured ChatOpenAI instance (or structured output runnable).
    """
    model_name = os.getenv("MODEL_NAME", "gpt-4o")
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE")
    temperature = float(os.getenv("TEMPERATURE", "0.6"))

    if not api_key:
        # We might want to raise an error or just warn, but letting LangChain handle it is usually fine
        pass

    if not base_url:
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
