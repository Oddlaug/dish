# -*- coding:utf-8 -*-
import os.path
import pickle
import pprint
from abc import ABCMeta, abstractmethod
from tkinter.messagebox import *
import sys


def get_int_number(input_message):
    while True:
        try:
            result = int(input(input_message))
            break

        except ValueError:
            print('Введите целое число!')
    return result


def check_name(_name):
    bad_symbols = [
            '\\', '/', ':', '*', '?', '\"',
            '<', '>', '|', '+', '%', '!', '@']

    for letter in _name:
        if letter in bad_symbols:
            print("Недопустимый символ \"%s\" в имени файла!" % letter)
            return False

    if _name.endswith(' '):
        print("В конце имени файла обнаружен пробел!")
        return False

    return True


class AbstractDataBase:
    __metaclass__ = ABCMeta

    def __init__(self, enc="utf-8"):
        self.__enc = enc

    @abstractmethod
    def create_db(self):
        raise NotImplementedError

    @abstractmethod
    def load_db(self):
        raise NotImplementedError

    @abstractmethod
    def update_db(self):
        raise NotImplementedError

    def export(self, content, destination):
        if check_name(destination):
            with open(destination, 'w', encoding=self.__enc) as dst:
                dst.write(content)


class DataBaseProcessor(AbstractDataBase):
    def __init__(self, db_file):
        super().__init__()
        self.__db_file = db_file
        self.__empty_db = {}
        self.__db_content = None

    @property
    def db_content(self):
        return self.__db_content

    def __create_db(self, content):
        with open(self.__db_file, 'wb') as f:
            pickle.dump(content, f)

    def create_db(self):
        if os.path.exists(self.__db_file):
            if askyesno("Файл уже существует!", "Перезаписать?"):
                self.__create_db(self.__empty_db)
        else:
            if check_name(self.__db_file):
                self.__create_db(self.__empty_db)

    def load_db(self):

        if os.path.exists(self.__db_file):
            try:

                with open(self.__db_file, 'rb') as f:
                    self.__db_content = pickle.load(f)
            except Exception as e:
                print(e)
        else:
            print("Файл \"{0}\"  не найден!".format(self.__db_file))

    def update_db(self):
        self.__create_db(self.__db_content)


class StringProcessor:
    def __init__(self):
        self.__result = []

    @property
    def result(self):
        return self.__result

    def convert_to_string(self, user_dict, sep=' | '):
        try:
            for key in user_dict:
                s = ""
                s += key + '\n'
                s += str(len(user_dict[key])) + '\n'

                for ingredient in user_dict[key]:
                    ingredient_list = []
                    ingredient_list.append(ingredient['ingredient_name'])
                    ingredient_list.append(str(ingredient['quantity']))
                    ingredient_list.append(ingredient['measure'])
                    s += sep.join(ingredient_list) + '\n'

                self.__result.append(s + '\n')

        except(AttributeError, KeyError) as e:
            print(e)


class CookBook(DataBaseProcessor, StringProcessor):
    def __init__(self, cook_book_file, export_file):
        DataBaseProcessor.__init__(self, cook_book_file)
        StringProcessor.__init__(self)
        self.__db_file = cook_book_file
        self.__export_file = export_file

    def create_cook_book(self):
        self.create_db()

    def add_recipe(self):
        self.load_db()
        another_dish = ""

        while another_dish.lower() != 'н':

            try:
                dish_name = input("Название блюда: ")

                dish = {dish_name: []}

                dish_parts = get_int_number("Количество ингредиентов: ")

                result = []

                for i in range(dish_parts):
                    ingredient_name = input('Название ингредиента:')

                    quantity = get_int_number('Количество:')

                    measure = input('Единицы измерения:')

                    one_component = {
                        'ingredient_name': ingredient_name,
                        'quantity': quantity,
                        'measure': measure, }

                    result.append(one_component)

                dish[dish_name].extend(result)
                self.db_content.update(dish)

            except KeyError:
                print("Такое блюдо уже есть!")

            another_dish = input("Добавить еще блюдо (д/н)?")

        self.update_db()

    def get_shop_list(self):

        person_count = get_int_number("Количество персон:")

        dishes = []
        choice = ''
        while choice.lower() != 'н':
            dishes.append(input("Название блюда: "))
            choice = input("Добавить еще название (д/н)?")

        self.load_db()

        result = {}

        try:
            for dish_name in dishes:

                for key in self.db_content[dish_name]:
                    one_dish = {}
                    key['quantity'] *= person_count
                    one_dish[key['ingredient_name']] = {
                                            'measure': key['measure'],
                                            'quantity': key['quantity']}
                    result.update(one_dish)
            print(result)

        except KeyError:
            print('Блюдо не найдено!!')

        pprint.pprint(result)

    def export_to_file(self):
        self.load_db()
        self.convert_to_string(self.db_content)
        content = ''.join(self.result)
        self.export(content, self.__export_file)

    def get_recipes(self):
        self.load_db()
        pprint.pprint(self.db_content)


if __name__ == "__main__":
    if (len(sys.argv)) == 3:
        cookbook = CookBook(sys.argv[1], sys.argv[2]) # db_name export_file_name
        cookbook.create_cook_book()
        cookbook.add_recipe()
        cookbook.get_shop_list()
        cookbook.export_to_file()
        cookbook.get_recipes()
    else:
        print("Input data error!")
