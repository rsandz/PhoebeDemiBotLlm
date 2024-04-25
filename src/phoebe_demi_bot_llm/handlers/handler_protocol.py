from typing import Protocol

from attr import dataclass

from phoebe_demi_bot_llm.models.context import Context


@dataclass
class HandlerResponse:
    """Response from a handler.

    Will end the handler chain.
    """

    response: str


@dataclass
class HandlerContinue:
    """Continue the handler chain."""

    pass


class HandlerProtocol(Protocol):
    """Protocol for handlers."""

    async def handle(self, context: Context) -> HandlerResponse | HandlerContinue:
        """Handle a context."""
        raise NotImplementedError
