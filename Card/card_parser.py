import asyncio
import logging

import aiohttp

import const
from Card.wild_catalog import WildCatalog
from Card.card_manipulator import CardManipulator
import SQL


class CardParser:
    def __init__(self, lite_connector: SQL.LiteConnector, catalog: dict, page=1):
        assert isinstance(catalog, dict), "Каталог для парсинга товаров должен быть словарем"
        assert isinstance(lite_connector, SQL.LiteConnector), "Каталог должен принимать экземпляр класса LiteConnector"
        self.card_session = aiohttp.ClientSession(headers=const.HEADERS)
        self.target_catalog = catalog
        self.page = page
        self.sleep = 2
        self.products = dict()
        self.parser_flag = True
        self.lite_connector = lite_connector
        self.card_manipulator = CardManipulator(self.lite_connector)

    async def parse(self):
        while self.parser_flag:
            await asyncio.sleep(self.sleep)
            self.update_layer()
            self.products = await self.get_products_json()
            self.check_layer()
            self.insert_products_in_db()

    def update_layer(self):
        """Обновляет состояние парсера. Получает последную страницу из БД"""
        self.page = self.card_manipulator.get_last_parsed_page() + 1
        pass

    def insert_products_in_db(self):
        """Вписывает товары в базу данных"""
        self.card_manipulator.insert_products(self.products, self.target_catalog['url'], self.page)
        pass

    def check_layer(self):
        """Проверяет ответ от сервера"""
        if not self.products:
            logging.info("Нет полученных товаров по ссылке")
            logging.info("CardParser перестает парсить товары")
            self.parser_flag = False
            return False

        logging.info(f"CardParser Получено товаров {len(self.products['data']['products'])} "
                     f"на старнице {self.page} "
                     f"для каталога {self.target_catalog['url']}")

    async def get_products_json(self):
        catalog_url = self.get_url_for_parse()
        try:
            resp_products = await self.card_session.get(catalog_url)
            assert resp_products.status == 200, f"Не удалось получить ответ по ссылке {catalog_url}"
            return await resp_products.json(encoding='utf8')
        except Exception as e:
            logging.info(e)

    def get_url_for_parse(self):
        cat_id = self.target_catalog['query']
        catalog_type = self.target_catalog['shard']
        catalog_url = f'https://catalog.wb.ru/catalog/{catalog_type}/catalog?appType=1&{cat_id}&curr=rub&page={self.page}&dest=-1268696&sort=popular&spp=0'
        return catalog_url

    async def close(self):
        await self.card_session.close()

    def __del__(self):
        asyncio.run(self.close())


async def main():
    logging.basicConfig(level=logging.INFO)
    lite_connector = SQL.LiteConnector('test')
    wb_catalog = WildCatalog('https://www.wildberries.ru/catalog/dom/mebel/detskaya-mebel')
    card_parser = CardParser(lite_connector, wb_catalog.catalog)
    task = asyncio.create_task(card_parser.parse())
    await task


if __name__ == '__main__':
    asyncio.run(main())