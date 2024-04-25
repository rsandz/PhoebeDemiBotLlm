import logging
from phoebe_demi_bot_llm.dao.throttle_dao import ThrottleDAO
from phoebe_demi_bot_llm.handlers.handler_protocol import HandlerContinue, HandlerResponse
from phoebe_demi_bot_llm.models.context import Context

logger = logging.getLogger(__name__)

class AllowlistHandler(object):
    def __init__(self, throttle_dao: ThrottleDAO):
        self.throttle_dao = throttle_dao

    async def handle(self, context: Context):
        user = context.user_name
        if self.throttle_dao.select_override_count_limit(user) == 0:
            logger.info(f"User {user} is not allowed to use llm.")
            return HandlerResponse("Sorry! You are not allowed to use this.")
        else:
            return HandlerContinue()

