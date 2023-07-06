import sqlite3
import re

from SQL.migrations import Migrate


class LiteConnector:
    _instance = None

    def __new__(csl, *args, **kwargs):
        if csl._instance is None:
            csl._instance = super().__new__(csl)
        return csl._instance

    def __init__(self, db_name: str):
        self.db_name = LiteConnector.check_db_name(db_name)
        self.cursor = sqlite3.connect(self.db_name).cursor()
        Migrate(self)

    @staticmethod
    def check_db_name(db_name: str):
        assert isinstance(db_name, str), f"Название базы должно быть строковым типом"
        assert re.search(r'.db', db_name), "Название базы данных должно содержать расширение .db"
        return db_name

    def commit(self):
        self.cursor.connection.commit()

    def __del__(self):
        self.close()

    def close(self):
        self.cursor.close()
        self.cursor.connection.close()


if __name__ == '__main__':
    lite_con = LiteConnector('test1')

