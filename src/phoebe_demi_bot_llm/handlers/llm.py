import logging
from typing import Callable, List

from langchain.agents import AgentExecutor
from langchain.tools import StructuredTool
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.utils.function_calling import convert_to_openai_function

from phoebe_demi_bot_llm.models.context import Context
from phoebe_demi_bot_llm.handlers.handler_protocol import HandlerResponse


logger = logging.getLogger(__name__)


class LlmHandler:

    def __init__(self, llm, chat_prompt, tools: List[Callable] = [], terminal_tools: List[Callable] = []):
        self.chat_prompt = chat_prompt
        self.tools = tools
        self.terminal_tools = terminal_tools

        converted_tools = [convert_to_openai_function(t) for t in self.tools]
        converted_terminal_tools = [convert_to_openai_function(t) for t in self.terminal_tools]

        llm_with_tools = llm.bind(
            functions = converted_tools + converted_terminal_tools
        )

        self.agent = (
            {
                "text": lambda x: x["text"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
            }
            | chat_prompt
            | llm_with_tools
            | OpenAIFunctionsAgentOutputParser()
        )

    def get_context_binded_tools(self, context: Context):
        context_binded_tools = []

        def bind_context_to_tool(tool, context):
            """Needed so that we don't close on loop variable"""
            def wrapped_tool():
                return tool(context)
            return wrapped_tool

        for t in self.tools:
            context_binded_tools.append(
                StructuredTool.from_function(
                    coroutine=bind_context_to_tool(t, context),
                    name=t.__name__,
                    description=t.__doc__ or "",
                )
            )

        for t in self.terminal_tools:
            context_binded_tools.append(
                StructuredTool.from_function(
                    coroutine=bind_context_to_tool(t, context),
                    name=t.__name__,
                    description=t.__doc__ or "",
                    return_direct=True,
                )
            )

        logger.info("Context binded tools: %s", context_binded_tools)
        return context_binded_tools

    async def handle(self, context: Context):

        context_binded_tools = self.get_context_binded_tools(context)

        agent_executor = AgentExecutor(
            agent=self.agent, tools=context_binded_tools, max_iterations=2, verbose=True  # type: ignore
        )

        output = (await agent_executor.ainvoke({"text": " ".join(context.msg)})).get(
            "output"
        )

        return HandlerResponse(response=output)  # type: ignore