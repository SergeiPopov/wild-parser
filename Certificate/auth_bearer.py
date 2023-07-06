import logging
from datetime import datetime

import requests

import const


class Bearer:
    def __init__(self):
        self.token = self.get_auth_token()
        self.token_time = datetime.now()

    def get_headers_with_auth(self):
        headers = const.HEADERS.copy()
        headers['Authorization'] = self.token
        return headers

    def get_auth_token(self):
        logging.info("Получаем токен авторизации для FSA")
        data = {'password': 'hrgesf7HDR67Bd', 'username': 'anonymous'}
        headers = {
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                   'Host': 'pub.fsa.gov.ru',
                   }
        token_response = requests.post('https://pub.fsa.gov.ru/login', json=data, headers=headers, verify=False, allow_redirects=True)
        assert token_response.status_code == 200, "Не удалось получить токен авторизации"
        print(token_response.headers)
        return token_response.headers['Authorization']

    def is_alive_token(self):
        logging.info("Проверка токена авторизации на актуальность")
        headers = self.get_headers_with_auth()
        is_alive_response = requests.get(f'https://pub.fsa.gov.ru/token/is/actual/{headers["Authorization"][7:]}', headers=headers, verify=False)
        assert is_alive_response.status_code == 200, "Не удалось узнать об актуальности токена"
        if 'true' in is_alive_response.text:
            logging.info("Проверка токена авторизации на актуальность - ПРОЙДЕНА")
            return True
        return False

    def check_token(self):
        minute_dif = (datetime.now() - self.token_time).seconds / 60
        if minute_dif > 30:
            if not self.is_alive_token():
                self.token = self.get_auth_token()
                self.check_token()
            self.token_time = datetime.now()


if __name__ == '__main__':
    auth = Bearer()
