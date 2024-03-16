from database_manager import DatabaseManager
from tkinter import ttk
from tabulate import tabulate

import tkinter as tk
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


class PhoneBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Book")

        logging.info("Application started")

        # Input fields
        tk.Label(root, text="First Name:").grid(row=0, column=0)
        self.first_name_var = tk.StringVar()
        first_name_entry = tk.Entry(root, textvariable=self.first_name_var)
        first_name_entry.grid(row=0, column=1)
        first_name_entry.bind('<Button-1>',
                              lambda x: self.first_name_var.set(""))

        tk.Label(root, text="Last Name:").grid(row=1, column=0)
        self.last_name_var = tk.StringVar()
        last_name_entry = tk.Entry(root, textvariable=self.last_name_var)
        last_name_entry.grid(row=1, column=1)
        last_name_entry.bind('<Button-1>',
                             lambda x: self.last_name_var.set(""))
        tk.Label(root, text="Phone Number:").grid(row=2, column=0)
        self.phone_number_var = tk.StringVar()
        tk.Entry(root, textvariable=self.phone_number_var).grid(row=2,
                                                                column=1)
        phone_entry = tk.Entry(root, textvariable=self.phone_number_var)
        phone_entry.grid(row=2, column=1)
        phone_entry.bind('<Button-1>',
                         lambda x: self.phone_number_var.set(""))
        # Address fields
        province_objects = database_manager.models['Provinces'].find()
        province_names = [province_object['province_name'] for province_object
                          in province_objects]
        tk.Label(root, text="Province:").grid(row=3, column=0)
        self.province_var = tk.StringVar()
        province_combobox = ttk.Combobox(root,
                                         textvariable=self.province_var,
                                         values=province_names)
        province_combobox.grid(row=3, column=1)

        tk.Label(root, text="City:").grid(row=4, column=0)
        self.city_var = tk.StringVar()
        self.city_combobox = ttk.Combobox(root,
                                          textvariable=self.city_var,
                                          values=list())
        self.city_combobox.grid(row=4, column=1)

        # Update cities based on province selection
        province_combobox.bind('<<ComboboxSelected>>',
                               lambda event: self.update_cities())

        # Buttons
        tk.Button(root, text="Save", command=self.save_contact).grid(row=5,
                                                                     column=0)
        tk.Button(root, text="Load Data In Terminal",
                  command=self.load_data).grid(row=5,
                                               column=1)
        self.clear_inputs()

    @staticmethod
    def all_data_table_print():
        """print all person's information in sentences"""
        table_list = list()
        phonebook = database_manager.models["PhoneBook"].find()
        for index, contact in enumerate(phonebook):
            table_data = [
                contact["first_name"],
                contact["last_name"],
                contact["phone_number"],
                contact["province"],
                contact["city"]
            ]
            table_list.append(table_data)
        table_str = tabulate(table_list,
                             headers=["First name",
                                      "Last name",
                                      "Phone number",
                                      "Province",
                                      "City"
                                      ]
                             )
        print(table_str)

    def info_to_dict(self):
        info_dict = dict()
        if self.first_name_var.get() != "Type first name in ENG":
            info_dict["first_name"] = self.first_name_var.get()
        else:
            raise (Exception("Please enter first name"))
        if self.last_name_var.get() != "Type last name in ENG":
            info_dict["last_name"] = self.last_name_var.get()
        else:
            raise (Exception("Please enter last name"))
        if self.phone_number_var.get() != "Type Phone Number":
            if len(self.phone_number_var.get()) > 11:
                raise (Exception("Please enter a valid phone number"))
            else:
                info_dict["phone_number"] = self.phone_number_var.get()
        else:
            raise (Exception("Please enter phone_number"))
        if self.province_var.get() != "Select Province":
            info_dict["province"] = self.province_var.get()
        else:
            raise (Exception("Please select province"))
        if self.city_var.get() != "Select City":
            info_dict["city"] = self.city_var.get()
        else:
            raise (Exception("Please select city"))

        return info_dict

    def clear_inputs(self):
        self.first_name_var.set("Type first name in ENG")
        self.last_name_var.set("Type last name in ENG")
        self.phone_number_var.set("Type Phone Number")
        self.province_var.set("Select Province")
        self.city_var.set("Select City")

    def save_contact(self):
        try:
            contact_info = self.info_to_dict()
            database_manager.models["PhoneBook"].insert_one(contact_info)
            self.clear_inputs()
            logging.info(f"Contact saved: {contact_info}")
        except Exception as e:
            logging.error(e)

    def load_data(self):
        try:
            self.all_data_table_print()
            logging.info("Data loaded successfully")
        except FileNotFoundError:
            logging.error("File not found.")
        except Exception as e:
            logging.error(e)

    def update_cities(self):
        province = self.province_var.get()
        # Assuming we have a predefined dictionary of provinces to cities
        province_query = {"admin_name": province}
        city_objects = database_manager.models["Cities"].find(province_query)
        city_names = [city_object["city"] for city_object in city_objects]
        self.city_combobox['values'] = city_names
        self.city_combobox.current()
        logging.info(f"Cities updated for province: {province}")


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

    root = tk.Tk()
    PhoneBookApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
