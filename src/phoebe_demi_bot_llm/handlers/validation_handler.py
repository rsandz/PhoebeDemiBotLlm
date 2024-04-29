from phoebe_demi_bot_llm.handlers.handler_protocol import (
    HandlerContinue,
    HandlerResponse,
)
from phoebe_demi_bot_llm.models.context import Context


class ValidationHandler:
    """Handler for validating context before passing to LLM."""

    def __init__(self, max_msg_length: int = 96):
        self.max_msg_length = max_msg_length

    async def handle(self, context: Context):
        if len(context.msg) > self.max_msg_length:
            return HandlerResponse(
                f"Sorry! Message is too long. (Must be less than {self.max_msg_length} characters)"
            )
        else:
            return HandlerContinue()
