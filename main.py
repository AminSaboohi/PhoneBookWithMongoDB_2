from database_manager import DatabaseManager

import local_settings
import logging

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


def main():



if __name__ == "__main__":
    main()