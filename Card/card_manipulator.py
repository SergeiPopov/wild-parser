from datetime import datetime

import SQL


class CardManipulator:
    def __init__(self, lite_connector: SQL.LiteConnector):
        self.lite_connector = lite_connector

    def get_last_parsed_page(self):
        last_page_sql = """SELECT card_page from card ORDER BY parse_date DESC LIMIT 1"""
        self.lite_connector.cursor.execute(last_page_sql)
        page = self.lite_connector.cursor.fetchone()
        return page[0] if page else 0

    def insert_products(self, products, card_catalog, page):
        if not products or not isinstance(products, dict) or not products.get('data') or not products['data'].get('products'):
            return False
        for product in products['data']['products']:
            if not self.check_product_by_id(product['id']):
                insert_prod_sql = f"""INSERT INTO card(card_id, card_catalog, card_url, card_name, card_brand, card_page, checked_certificate, parse_date)
                                        VALUES(?, ?, ?, ?, ?, ?, ?, ?)"""
                params = (product['id'],
                          card_catalog,
                          f'https://www.wildberries.ru/catalog/{product["id"]}/detail.aspx',
                          product['name'],
                          product['brand'],
                          page,
                          0,
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                self.lite_connector.cursor.execute(insert_prod_sql, params)
                self.lite_connector.commit()
        return True

    def get_unchecked_card(self):
        unchecked_card_sql = """SELECT * from card WHERE checked_certificate = 0"""
        self.lite_connector.cursor.execute(unchecked_card_sql)
        return self.lite_connector.cursor.fetchone()

    def update_flag_in_card_by_id(self, id):
        check_certificate_sql = f"""UPDATE card SET checked_certificate = 1 WHERE card_id = {id}"""
        self.lite_connector.cursor.execute(check_certificate_sql)
        self.lite_connector.commit()
        return True

    def check_product_by_id(self, id):
        check_prod_sql = f"""SELECT * from card WHERE card_id = {id}"""
        self.lite_connector.cursor.execute(check_prod_sql)
        return True if self.lite_connector.cursor.fetchone() else False
