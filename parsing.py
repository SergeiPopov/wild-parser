import asyncio
import logging
import re
import time

import aioconsole

import SQL
import Certificate
import Card
from CSVMaker import *


async def close_parser(db_name, catalog_name):
    print('Для выхода из программы напишите exit в консоле и нажмите ENTER\n')
    print('Парсинг начинается...\n')
    time.sleep(5)
    line = ''
    while line != 'exit':
        line = await aioconsole.ainput("Введите команду exit для остановки парсера\n")
    lite_con = SQL.LiteConnector(db_name)
    csv_name = catalog_name[re.search(r'catalog', catalog_name).start():].replace('/', '_')
    CSVMaker(lite_con, csv_name+'.csv')
    print(f"Для сохранения результатов был создан csv файл {csv_name}\n")
    input("Нажмите любую клавишу...\n")
    exit(0)


async def main(db_name, catalog_name):
    lite_con = SQL.LiteConnector(db_name)
    wb_catalog = Card.WildCatalog(catalog_name)
    card_parser = Card.CardParser(lite_con, wb_catalog.catalog)
    cert_parser = Certificate.FSAParser(lite_con)
    close_task = asyncio.create_task(close_parser(db_name, catalog_name))
    card_task = asyncio.create_task(card_parser.parse())
    cert_task = asyncio.create_task(cert_parser.parse())
    await close_task
    await card_task
    await cert_task


if __name__ == '__main__':
    db_name = input("Введите название базы для записи товаров и сертификатов с раширением .db. Например, 'det_mebel.db' - ")
    catalog_name = input("Введите ссылку на каталог WB. Например, 'https://www.wildberries.ru/catalog/dom/mebel/detskaya-mebel' - ")
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main(db_name, catalog_name))
    except Exception as e:
        print(e)
        input("Возникла ошибка или программа закончила своё выпонение. Нажмите любую клавишу для выхода...")
