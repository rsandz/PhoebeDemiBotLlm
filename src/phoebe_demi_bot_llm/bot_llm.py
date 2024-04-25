import asyncio
import logging
from langchain.globals import set_debug, set_verbose

from models.context import Context

from dotenv import load_dotenv

from dispatcher import LlmDispatcher

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
