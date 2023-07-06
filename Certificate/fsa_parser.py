import asyncio
import logging
import re

import aiohttp

import Card
import Certificate
import SQL


class FSAParser:
    def __init__(self, lite_connector: SQL.LiteConnector):
        assert isinstance(lite_connector, SQL.LiteConnector), "Парсер должен принимать экземпляр класса LiteConnector"
        self.lite_connector = lite_connector
        self.parse_flag = True
        self.sleep = 2
        self.authorization = Certificate.Bearer()
        self.card_manipulator = Card.CardManipulator(self.lite_connector)
        self.cert_manipulator = Certificate.CertManipulator(self.lite_connector)
        headers_with_auth = self.authorization.get_headers_with_auth()
        self.fsa_session = aiohttp.ClientSession(headers=headers_with_auth, connector=aiohttp.TCPConnector(ssl=False))

    async def parse(self):
        count_checked_urls = 0
        while self.parse_flag:
            count_checked_urls += 1
            self.authorization.check_token()
            await self.get_fsa_cert_from_cards()
            if count_checked_urls % 10 == 0:
                logging.info(f"Проверено ссылок за сессию {count_checked_urls}")

    async def get_fsa_cert_from_cards(self):
        unchecked_card = self.card_manipulator.get_unchecked_card()
        if unchecked_card:
            logging.info(f"Проверяется товар на сертификат под номером {unchecked_card[0]} {unchecked_card[3]}")
            card_id = unchecked_card[0]
            json_cert_response = await self.check_fsa_cert(card_id)
            fsa_cert = await self.get_fsa_certificate(json_cert_response)
            self.insert_certificate(fsa_cert, card_id, json_cert_response)
        else:
            logging.info(f"Нет непроверенных товаров на сертификат. Пожалуйста добавьте записей из каталога в базу данных")
            await asyncio.sleep(20)

    async def check_fsa_cert(self, card_id):
        await asyncio.sleep(self.sleep)
        wild_cert_url = self.get_url_for_card_by_id(card_id)
        wild_cert_response = await self.fsa_session.get(wild_cert_url)
        self.card_manipulator.update_flag_in_card_by_id(card_id)
        if wild_cert_response.status == 200:
            wild_json = await wild_cert_response.json()
            logging.info(f"Сертификат на товар {card_id} - {wild_json.get('url')}")
            return wild_json
        return None

    async def get_fsa_certificate(self, json_cert_response):
        await asyncio.sleep(self.sleep)
        if not json_cert_response:
            return None
        fsa_url = json_cert_response['url']
        cert_id = re.search(r'\d+', fsa_url).group(0)
        cert_group = re.search(r'(rds|rss)', fsa_url).group(0)
        cert_type = re.search(r'(certificate|declaration)', fsa_url).group(0)
        fsa_api_url = f'https://pub.fsa.gov.ru/api/v1/{cert_group}/common/{cert_type}s/{cert_id}'
        logging.info(f"Получение сертификата по ссылке.... {fsa_api_url}")
        fsa_response = await self.fsa_session.get(fsa_api_url)
        assert fsa_response.status == 200, f'не удалось получить ответ от FSA API по ссулке {fsa_api_url}'
        return await fsa_response.json(encoding='utf8')

    def insert_certificate(self, fsa_cert, card_id, json_cert_response):
        if not fsa_cert:
            return None
        self.cert_manipulator.insert_cert_from_parser(fsa_cert, card_id, json_cert_response['url'])

    def get_url_for_card_by_id(self, id: int):
        n = id
        r = ~~int(n/1e5)
        o = ~~int(n/1e3)
        return 'https:' + self.get_basket(r) + f'vol{r}/part{o}/{n}' + '/info/certificate.json'

    def get_basket(self, e):
        if e >= 0 and e <= 143:
            return "//basket-01.wb.ru/"
        elif e >= 144 and e <= 287:
            return "//basket-02.wb.ru/"
        elif e >= 288 and e <= 431:
            return "//basket-03.wb.ru/"
        elif e >= 432 and e <= 719:
            return "//basket-04.wb.ru/"
        elif e >= 720 and e <= 1007:
            return "//basket-05.wb.ru/"
        elif e >= 1008 and e <= 1061:
            return "//basket-06.wb.ru/"
        elif e >= 1062 and e <= 1115:
            return "//basket-07.wb.ru/"
        elif e >= 1116 and e <= 1169:
            return "//basket-08.wb.ru/"
        elif e >= 1170 and e <= 1313:
            return "//basket-09.wb.ru/"
        elif e >= 1314 and e <= 1601:
            return "//basket-10.wb.ru/"
        elif e >= 1602 and e <= 1655:
            return "//basket-11.wb.ru/"
        elif e >= 1656 and e <= 1919:
            return "//basket-12.wb.ru/"
        else:
            return "//basket-13.wb.ru/"

    async def close(self):
        await self.fsa_session.close()

    def __del__(self):
        asyncio.run(self.close())


async def main():
    logging.basicConfig(level=logging.INFO)
    lite_con = SQL.LiteConnector('test_auto_created.db')
    fsa_parser = FSAParser(lite_con)
    fsa_parser_task = asyncio.create_task(fsa_parser.parse())
    await fsa_parser_task


if __name__ == '__main__':
    asyncio.run(main())