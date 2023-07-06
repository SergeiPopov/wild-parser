import re
import json


class WildCatalog:
    def __init__(self, user_url_catalog: str, catalog_path='./Card/catalog.json'):
        self.catalog_path = catalog_path
        self.catalog = self.define_catalog_from_url(user_url_catalog)

    def define_catalog_from_url(self, user_url_catalog: str):
        assert isinstance(user_url_catalog, str) and re.search(r'/catalog\S+', user_url_catalog), "Ссылка на каталог должна быть строкой и содеражать название каталога catalog/<catalog_name>"
        catalog_url = re.search(r'/catalog\S+', user_url_catalog).group(0)
        return self.search_catalog_from_json(catalog_url)

    def get_catalog_json(self):
        with open(self.catalog_path, 'r', encoding='utf8') as catalog_json_file:
            return json.loads(catalog_json_file.read())

    def search_catalog_from_json(self, catalog_url: str):
        catalog_json = self.get_catalog_json()
        catalog = list()
        self.recursive_search(catalog_json, catalog_url, catalog)
        assert catalog, f'Не удалось найти каталог {catalog_url} в словаре'
        return catalog[0]

    def recursive_search(self, catalog_json, catalog_url: str, result_catalog):
        for catalog in catalog_json:
            if len(result_catalog) != 0:
                break

            if catalog['url'] == catalog_url:
                catalog['childs'] = list()
                result_catalog.append(catalog)
                return catalog

            if catalog.get('childs'):
                self.recursive_search(catalog.get('childs'), catalog_url, result_catalog)


if __name__ == '__main__':
    wb_catalog = WildCatalog('https://www.wildberries.ru/catalog/dom/mebel/detskaya-mebel')
    print(wb_catalog.catalog)