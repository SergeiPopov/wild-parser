import logging


class Migrate:
    def __init__(self, connector):
        self.connector = connector
        self.check_tables()

    def check_tables(self):
        exist_tables = Migrate.get_table_from_connector(self.connector)
        target_tables = list(self.migrate_tables().keys())
        count_exist_tables = 0
        for table in target_tables:
            if table in exist_tables:
                count_exist_tables += 1

        if count_exist_tables == len(target_tables):
            logging.info(f"В базе данных {self.connector.db_name} уже существуют все нужные таблицы")
            return True

        if count_exist_tables == 0:
            logging.info(f"Применяются миграции по создании всех нужных таблиц: {' '.join(target_tables)} для {self.connector.db_name}")
        else:
            logging.info(f"В базе данных {self.connector.db_name} уже существует часть таблиц.")
        self.make_migrations()

    def migrate_tables(self) -> dict:
        return {'card': self.create_card_table(), 'certificate': self.create_certificate_table()}

    @staticmethod
    def get_table_from_connector(connector):
        connector.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in connector.cursor.fetchall()]

    def make_migrations(self):
        for table_name, create_table_query in self.migrate_tables().items():
            self.connector.cursor.execute(create_table_query)
            self.connector.cursor.connection.commit()

    def create_certificate_table(self) -> str:
        certificate_table = """
            CREATE TABLE IF NOT EXISTS certificate (
                certificate_id integer PRIMARY KEY,
                certificate_url text NOT NULL,
                certificate_number text NOT NULL,
                certRegDate text NOT NULL,
                certEndDate text NOT NULL,
                FIO text NOT NULL,
                org_name text NOT NULL,
                org_email text NOT NULL,
                org_mobile_number text NOT NULL,
                org_other_contact text NOT NULL,
                org_address text NOT NULL,
                parse_date datetime NOT NULL,
                card_id integer NOT NULL,
                           
                FOREIGN KEY (card_id) REFERENCES card (card_id)
            );
        """
        return certificate_table

    def create_card_table(self) -> str:
        card_table = """
            CREATE TABLE IF NOT EXISTS card (
                card_id integer PRIMARY KEY,
                card_catalog text NOT NULL,
                card_url text NOT NULL,
                card_name text NOT NULL,
                card_brand text NOT NULL,
                card_page integer NOT NULL,
                checked_certificate integer NOT NULL,
                parse_date datetime NOT NULL
            );
        """
        return card_table