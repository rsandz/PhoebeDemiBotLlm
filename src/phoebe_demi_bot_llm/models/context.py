from dataclasses import dataclass
from typing import Any


@dataclass
class Context:
    """Context used to invoke the LLM dispatcher."""

    user_name: str
    """The name of the user."""

    msg: str
    """The message sent by the user."""

    discord_context: Any
    """The context of the Discord message."""
