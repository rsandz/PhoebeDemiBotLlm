import datetime
from venv import logger

import logging

from phoebe_demi_bot_llm.dao.throttle_dao import ThrottleDAO
from phoebe_demi_bot_llm.handlers.handler_protocol import (
    HandlerContinue,
    HandlerResponse,
)
from phoebe_demi_bot_llm.models.context import Context

logger = logging.getLogger(__name__)


class ThrottleHandler:

    LOOK_BACK_HOURS = 12
    DEFAULT_COUNT_LIMIT = 24

    def __init__(self, throttle_dao: ThrottleDAO):

        self.throttle_dao = throttle_dao

    async def handle(self, context: Context):
        user = context.user_name
        self.throttle_dao.insert_frequency_count(user, datetime.datetime.now())
        logger.info(f"Recorded call for {user}")

        count = self.throttle_dao.select_frequency_count(user, self.LOOK_BACK_HOURS)
        logger.info("Count for user %s: %s", user, count)

        count_limit = (
            self.throttle_dao.select_override_count_limit(user)
            or self.DEFAULT_COUNT_LIMIT
        )
        logger.info("Count limit for user %s: %s", user, count_limit)

        if count >= count_limit:
            return HandlerResponse(
                response=f"Sorry! You've used the LLM too many times ({self.DEFAULT_COUNT_LIMIT}) in the last {self.LOOK_BACK_HOURS} hours. Please try again later."
            )
        else:
            return HandlerContinue()
