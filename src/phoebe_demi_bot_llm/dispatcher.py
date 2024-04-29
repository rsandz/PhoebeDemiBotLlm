import sqlite3
from typing import Awaitable, Callable, List, Sequence

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.globals import set_debug, set_verbose

from phoebe_demi_bot_llm.dao.throttle_dao import ThrottleDAO
from phoebe_demi_bot_llm.handlers.allowlist_handler import AllowlistHandler
from phoebe_demi_bot_llm.handlers.handler_protocol import (
    HandlerContinue,
    HandlerProtocol,
    HandlerResponse,
)
from .handlers.llm import LlmHandler
from .handlers.throttle_handler import ThrottleHandler
from phoebe_demi_bot_llm.models.context import Context


class LlmDispatcher:
    """Process user messages via LLM with guardrails."""

    DEFAULT_PROMPT = """
    You are a helpful discord bot. You play as 2 characters: Phoebe and Demi.
    Answer in a light hearted manner with liberal use of emojis.
    If you don't know the answer to a question or can't help, just say that you don't know.
    """

    def __init__(
        self,
        llm=None,
        bot_prompt=DEFAULT_PROMPT,
        tools: Sequence[Callable[[Context], Awaitable]] = [],
        terminal_tools: Sequence[Callable[[Context], Awaitable]] = [],
        db_name="bot_llm.db",
    ):
        """Initialize LlmDispatcher.

        Args:
            llm: Language Model to use.
            bot_prompt: Prompt to that describes the bot and what it does.
            tools: List of tools to use. Must be async and have 1 arg that is context.
            terminal_tools: List of tools that will terminate LLM once ran.
                Must be async and have 1 arg that is context.
            db_name: Name of database to use.
        """
        if not llm:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        else:
            self.llm = llm
        self.tools = tools

        human_template = "{text}"
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", bot_prompt),
                ("user", human_template),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        db = sqlite3.connect(db_name)
        throttle_dao = ThrottleDAO(db)

        self.handler_chain: List[HandlerProtocol] = [
            AllowlistHandler(throttle_dao),
            ThrottleHandler(throttle_dao),
            LlmHandler(
                llm=self.llm,
                chat_prompt=chat_prompt,
                tools=tools,
                terminal_tools=terminal_tools,
            ),
        ]

    async def invoke(self, context):
        """Invokes the dispatcher to process a message in context via LLM.

        Args:
            context: The context to be passed to each handler.

        Returns:
            None
        """
        for handler in self.handler_chain:
            output = await handler.handle(context)

            if isinstance(output, HandlerResponse):
                return output.response
            elif isinstance(output, HandlerContinue):
                continue

    def set_debug(self, bool):
        set_debug(bool)
        set_verbose(bool)
