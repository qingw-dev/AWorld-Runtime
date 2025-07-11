"""AWorld Runtime."""

from dotenv import load_dotenv

from . import openrouter

__all__ = ["openrouter"]

load_dotenv()
