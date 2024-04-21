from dataclasses import dataclass
from typing import Any


@dataclass
class Context:
    user_name: str
    msg: str
    discord_context: Any
