import sqlite3
import datetime


class ThrottleDAO:
    def __init__(self, db_connection):
        self.db = db_connection
        self.create_tables()

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
        self.db.commit()

    def insert_frequency_count(self, user, date):
        insert_sql = """
        INSERT INTO frequency_count (user_name, date) VALUES (?, ?)
        """
        self.db.execute(insert_sql, (user, date))
        self.db.commit()

    def select_frequency_count(self, user, look_back_hours):
        select_sql = f"""
        SELECT COUNT(*) FROM frequency_count 
        WHERE user_name = ? AND date > DATETIME('now', '-{look_back_hours} hours')
        """
        return self.db.execute(select_sql, (user,)).fetchone()[0]

    def select_override_count_limit(self, user):
        select_sql = """
        SELECT amount FROM override_users WHERE user_name = ?
        """
        result = self.db.execute(select_sql, (user,)).fetchone()
        if result:
            return result[0]
        else:
            return None

    def insert_override_count_limit(self, user, amount):
        insert_sql = """
        INSERT OR REPLACE INTO override_users (user_name, amount) VALUES (?, ?)
        """
        self.db.execute(insert_sql, (user, amount))
        self.db.commit()
