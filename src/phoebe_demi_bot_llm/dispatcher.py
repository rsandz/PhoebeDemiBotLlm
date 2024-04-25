import sqlite3
from typing import Callable, List

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
from phoebe_demi_bot_llm.handlers.llm import LlmHandler
from phoebe_demi_bot_llm.handlers.throttle_handler import ThrottleHandler


class LlmDispatcher:

    DEFAULT_PROMPT = """
    You are a helpful discord bot. You play as 2 characters: Phoebe and Demi.
    Answer in a light hearted manner with liberal use of emojis.
    If you don't know the answer to a question or can't help, just say that you don't know.
    """

    def __init__(
        self,
        llm=None,
        bot_prompt=DEFAULT_PROMPT,
        tools: List[Callable] = [],
        terminal_tools: List[Callable] = [],
        db_name = "bot_llm.db"
    ):
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
        for handler in self.handler_chain:
            output = await handler.handle(context)

            if isinstance(output, HandlerResponse):
                return output.response
            elif isinstance(output, HandlerContinue):
                continue

    def set_debug(self, bool):
        set_debug(bool)
        set_verbose(bool)
