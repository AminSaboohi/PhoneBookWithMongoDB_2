from database_manager import DatabaseManager

import local_settings
import logging
import os
import json

database_manager = DatabaseManager(
    host=local_settings.DATABASE['host'],
    port=local_settings.DATABASE['port'],
    database_name=local_settings.DATABASE['name']
)

mongodb_database = database_manager.mongodb_database

database_manager.create_collections(['PhoneBook',
                                     'Cities',
                                     'Provinces',
                                     ])


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


def log_decorator(func):
    def wrapper(*args, **kwargs):
        logging.info(f"{func.__name__} was called")
        return func(*args, **kwargs)

    return wrapper


class CityProvinceQuery:
    def __init__(self, base_path):
        self.provinces = list()
        cities_file_path = os.path.join(base_path, 'ir.json')

        with open(cities_file_path, 'r', encoding='utf-8') as cities_file:
            self.cities = json.load(cities_file)

    def get_all_cities(self):
        return self.cities

    def get_all_provinces(self):
        self.provinces = list()
        for city in self.cities:
            if city["admin_name"] not in self.provinces:
                province_dict = {'province_name': city["admin_name"]}
                self.provinces.append(province_dict)
        return self.provinces


def read_all_provinces_and_add_to_db(path: str = "./city and province json/"):
    city_province = CityProvinceQuery(path)
    provinces = city_province.get_all_provinces()
    database_manager.models["Provinces"].insert_many(provinces)


def read_all_cities_and_add_to_db(path: str = "./city_and province json/"):
    city_province = CityProvinceQuery(path)
    cities = city_province.get_all_cities()
    database_manager.models["Cities"].insert_many(cities)


def main():
    try:
        read_all_cities_and_add_to_db("./city and province json/")
        read_all_provinces_and_add_to_db("./city and province json/")
    except Exception as error:
        print("Error", error)


if __name__ == "__main__":
    main()
