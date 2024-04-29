"""Script used to test the package locally.

Run via `python3 -m phoebe_demi_bot_llm.bot_llm`
"""

import asyncio
import logging
from langchain.globals import set_debug, set_verbose

from phoebe_demi_bot_llm.models.context import Context
from phoebe_demi_bot_llm.dispatcher import LlmDispatcher

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    set_debug(False)
    set_verbose(False)
    if not load_dotenv():
        logger.error("Error loading .env file")
        exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    msg = input(">>> ")
    context = Context(
        user_name="tesat_user",
        msg=msg,
        discord_context=None,
    )

    async def my_points(ctx):
        "Returns my points"
        return 100

    dispatcher = LlmDispatcher(tools=[my_points])

    output = asyncio.run(dispatcher.invoke(context))
    logger.info("Response: %s", output)
else:
    set_debug(False)
