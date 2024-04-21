import datetime
from venv import logger
import sqlite3

import logging

from phoebe_demi_bot_llm.handlers.handler_protocol import HandlerContinue, HandlerResponse
from phoebe_demi_bot_llm.models.context import Context

logger = logging.getLogger(__name__)


class ThrottleHandler:

    LOOK_BACK_HOURS = 12
    DEFAULT_COUNT_LIMIT = 24

    def __init__(self):
        self.db = sqlite3.connect("bot_llm.db")
        self.create_tables()

        # Default Overrides
        override_sql = """
        INSERT OR REPLACE INTO override_users (user_name, amount) VALUES (?, ?)
        """
        self.db.execute(override_sql, ("test_user", 999))

    def create_tables(self):
        create_frequency_table_sql = """
        CREATE TABLE IF NOT EXISTS frequency_count (user_name TEXT, date Date);
        """
        self.db.execute(create_frequency_table_sql)

        create_override_table_sql = """
        CREATE TABLE IF NOT EXISTS override_users (user_name TEXT PRIMARY KEY, amount INTEGER);
        """
        self.db.execute(create_override_table_sql)

        trigger_sql = """
        CREATE TRIGGER IF NOT EXISTS delete_expired_rows
        AFTER INSERT ON frequency_count
        BEGIN
            DELETE FROM frequency_count WHERE date < DATETIME('now', '-30 day');
        END;
        """
        self.db.execute(trigger_sql)

    def record_call(self, user):
        insert_sql = """
        INSERT INTO frequency_count (user_name, date) VALUES (?, ?)
        """
        self.db.execute(insert_sql, (user, datetime.datetime.now()))
        self.db.commit()

    def get_count(self, user, look_back_hours):
        select_sql = f"""
        SELECT COUNT(*) FROM frequency_count 
        WHERE user_name = ? AND date > DATETIME('now', '-{look_back_hours} hours')
        """
        return self.db.execute(select_sql, (user,)).fetchone()[0]

    def get_override_count_limit(self, user):
        select_sql = """
        SELECT amount FROM override_users WHERE user_name = ?
        """
        result = self.db.execute(select_sql, (user,)).fetchone()
        if result:
            return result[0]
        else:
            return None

    async def handle(self, context: Context):
        user = context.user_name
        self.record_call(user)
        logger.info(f"Recorded call for {user}")

        count = self.get_count(user, self.LOOK_BACK_HOURS)
        logger.info("Count for user %s: %s", user, count)

        count_limit = self.get_override_count_limit(user) or self.DEFAULT_COUNT_LIMIT
        logger.info("Count limit for user %s: %s", user, count_limit)

        if count >= count_limit:
            return HandlerResponse(
                response=f"Sorry! You've used the LLM too many times ({self.DEFAULT_COUNT_LIMIT}) in the last {self.LOOK_BACK_HOURS} hours. Please try again later."
            )
        else:
            return HandlerContinue()
