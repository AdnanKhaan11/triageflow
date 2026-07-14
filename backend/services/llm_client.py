from __future__ import annotations
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()


"""
backend/services/llm_client.py

RESPONSIBILITY
---------------
A single, central place that knows how to talk to your chosen LLM
provider. Every agent (classifier, drafting) should call through this
wrapper rather than importing a provider SDK directly — this is what
lets you swap providers/models later (e.g. dev with a cheap model,
demo with a better one) by changing ONE file instead of four.
"""


def get_chat_model(model_name: str | None = None) -> ChatGroq:
    """
    Returns a configured chat model instance, reading API keys
    from environment variables (never hard-code keys -- see
    .env.example).
    """
    api_key = os.getenv("GROQ_API_KEY")
    MODEL_NAME = model_name or os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

    llm = ChatGroq(
        model=MODEL_NAME,
        api_key=api_key,
        temperature=0.3,
        max_retries=3,
        timeout=30,
    )

    return llm
