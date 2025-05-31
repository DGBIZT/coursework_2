import requests
from abc import ABC, abstractmethod
import os
import json
from pathlib import Path


class VacancyApi(ABC):

    @abstractmethod
    def __load_vacancies(self, keyword):
        pass

    @abstractmethod
    def file_writer_base(self):
        pass

class FileStorage(ABC):
    # Абстрактный класс на добавление вакансии add_vacancy,
    # получение данных из файла по указанным критериям get_vacancies,
    # удаление информации о вакансиях delete_vacancy
    @abstractmethod
    def add_vacancy(self, vacancy_job):
        pass

    @abstractmethod
    def get_vacancies(self, criteria):
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy_id):
        pass

class HH(VacancyApi):
    """
    Класс для работы с API HeadHunter
    """

    def __init__(self):

        self.__url = 'https://api.hh.ru/vacancies'
        self.__headers = {'User-Agent': 'HH-User-Agent'}
        self.__params = {'text': '', 'page': 0, 'per_page': 100, "area": "113"}
        self.__vacancies = []

    def _VacancyApi__load_vacancies(self, keyword):
        self.__params['text'] = keyword.lower()
        while self.__params.get('page') < 20:
            response = requests.get(self.__url, headers=self.__headers, params=self.__params)
            if response.status_code == 200:
                vacancies = response.json()['items']
                self.__vacancies.extend(vacancies)
                self.__params['page'] += 1
                # Добавляем проверку на количество страниц
                if response.json().get('pages') <= self.__params['page']:
                    break
            else:
                raise Exception(f"Ошибка при запросе к API: {response.status_code}")

    def get_vacancies(self):
        return self.__vacancies

    def file_writer_base(self):
        # Создаем директорию data, если она не существует
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)

        # Формируем полный путь к файлу
        file_path = os.path.join(data_dir, "vacancies.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.__vacancies,f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка записи в файл: {e}")


class Vacancy:
    __slots__ = ("name_vacancy", "url_vacancy", "__salary", "town", "snippet")
    """
    Класс для работы с вакансиями
    """
    # def __init__(self, name_vacancy, url_vacancy, salary, town, snippet):
    #     self.name_vacancy = name_vacancy.get("name")
    #     self.url_vacancy = url_vacancy.get('alternate_url')
    #     self.__salary = salary.get('from') if salary else 0
    #     self.town = town.get('name')
    #     self.snippet = snippet.get("snippet").get('requirement')

    def __init__(self, data):
        self.name_vacancy = data.get('name', '')
        self.url_vacancy = data.get('alternate_url', '')
        salary_data = data.get('salary')
        self.__salary = salary_data.get('from', 0) if salary_data else 0
        self.town = data.get('area', {}).get('name', '')
        self.snippet = data.get('snippet', {}).get('requirement', '')

    @property
    def salary(self):
        return self.__salary

    def __str__(self):
        return f"{self.name_vacancy} {self.url_vacancy} {self.__salary} {self.town} {self.snippet}"

    def __eq__(self, other):
        """__eq__ - equal означает равно"""
        if isinstance(other, Vacancy):
            return self.__salary == other.__salary
        return NotImplemented

    def __ge__(self, other):
        """__ge__ - greater than or equal означает больше или равно"""
        if isinstance(other,Vacancy):
            return self.__salary >= other.__salary
        return NotImplemented

    def matches_keywords(self, keywords):
        """Фильтрация по ключевым словам"""
        text = f"{self.name_vacancy.lower()} {self.snippet.lower()}{self.town.lower()}"
        return any(word in text for word in keywords)

    @staticmethod
    def top_number(vacancies, number):
        """
        Возвращает топ N вакансий по зарплате
        :param vacancies: список объектов Vacancy
        :param number: количество вакансий для вывода
        :return: список топ N вакансий
        """
        return vacancies[:number + 1]

    @staticmethod
    def salary_range(vacancies, salary_range):
        """
        Фильтрует вакансии по указанному диапазону зарплат
        :param vacancies: список вакансий
        :param salary_range: кортеж с минимальным и максимальным значением зарплаты (min_salary, max_salary)
        :return: список подходящих вакансий
        """
        # Проверяем корректность входных данных
        if not isinstance(salary_range, tuple) or len(salary_range) != 2:
            raise ValueError("Диапазон зарплат должен быть кортежем из двух чисел")

        min_salary, max_salary = salary_range
        # Проверяем, что оба значения числа
        if not isinstance(min_salary, (int, float)) or not isinstance(max_salary, (int, float)):
            raise TypeError("Значения диапазона зарплат должны быть числами")

        # Фильтруем вакансии по диапазону зарплат
        filtered_vacancies = [
            vacancy
            for vacancy in vacancies
            if min_salary <= vacancy.salary <= max_salary
        ]

        return filtered_vacancies



class JsonVacancyManager(FileStorage):

    def __init__(self, filename="data/vacancies.json"):
        self.__filename = filename

    def add_vacancy(self, vacancy_job):
        """Добавление вакансии"""
        try:
            with open(self.__filename, "r+", encoding="utf-8" ) as file:
                data = json.load(file) #Преобразование JSON-строки в Python-объект
                if vacancy_job not in data:
                    data.append(vacancy_job)
                    file.seek(0) # Перемещение указателя файла в начало файла. Необходимо для перезаписи всего файла. Без этого данные были бы записаны в конец файла
                    json.dump(data, file) #Преобразование Python-объекта обратно в JSON
                else:
                    return "Данная вакансия уже существует"
        except json.JSONDecodeError:
            return "Ошибка декодирования JSON"
        except Exception as e:
            return f"Произошла ошибка: {str(e)}"

    def get_vacancies(self, criteria):
        """ Получение данных из файла по указанным критериям """
        try:
            with open(self.__filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                result = list()
                for v in data:
                    if criteria(v):
                        result.append(v)
                return result
        except FileNotFoundError:
            print("Файл не найден")
            return []
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON")
            return []
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
            return []

    def delete_vacancy(self, vacancy_id):
        """Удаление вакансии"""
        try:
            with open(self.__filename, 'r+', encoding="utf-8") as file:
                data = json.load(file)
                data = [v for v in data if v.get('id') != vacancy_id]
                file.seek(0)
                file.truncate()
                json.dump(data, file, ensure_ascii=False, indent=2)
        except FileNotFoundError:
            raise FileNotFoundError("Файл с вакансиями не найден")
        except Exception as e:
            raise Exception(f"Произошла ошибка при удалении вакансии: {str(e)}")

if __name__ == '__main__':
    vacancies_list = []  # Создаем список для хранения объектов

    hh_parser = HH()
    hh_parser._VacancyApi__load_vacancies("Водитель")
    vacancies_data = hh_parser.get_vacancies()
    hh_parser.file_writer_base()


    # Создаем объекты и добавляем их в список
    for vacancy in vacancies_data:
        new_vacancy = Vacancy(vacancy)  # Передаем всю вакансию как один параметр
        vacancies_list.append(new_vacancy)


    # Сортируем список по зарплате
    sorted_vacancies = sorted(vacancies_list, key=lambda v: v.salary, reverse=True)
    filter_words = input("Введите ключевые слова для фильтрации вакансий: ").lower().split()

    # Фильтруем список вакансий
    filtered_vacancies = []
    for vacancy in sorted_vacancies:
        if vacancy.matches_keywords(filter_words):
            filtered_vacancies.append(vacancy)

    # Выводим отсортированные вакансии
    for vacancy in filtered_vacancies:
        print(vacancy)
        print("-" * 50)  # Разделитель между вакансиями

    # for vacancy in vacancies_data:
    #     new_vacancy = Vacancy(vacancy)
    #     vacancies_list.append(new_vacancy)

    # if len(vacancies_list) >= 2:
    #     vacancy1_data = vacancies_list[0]
    #     vacancy2_data = vacancies_list[1]
    #
    #     vacancy1 = Vacancy(
    #         name_vacancy=vacancy1_data,
    #         url_vacancy=vacancy1_data,
    #         salary=vacancy1_data.get('salary'),
    #         town=vacancy1_data.get('area'),
    #         snippet=vacancy1_data
    #     )
    #     vacancy2 = Vacancy(
    #         name_vacancy=vacancy2_data,
    #         url_vacancy=vacancy2_data,
    #         salary=vacancy2_data.get('salary'),
    #         town=vacancy2_data.get('area'),
    #         snippet=vacancy2_data
    #     )
    # #
    #     if vacancy1 == vacancy2:
    #         print("Зарплаты равны")
    #     else:
    #         print(f"Зарплаты отличаются:{"\n"} {vacancy1.name_vacancy} {vacancy1.salary}{"\n"} {vacancy2.name_vacancy} {vacancy2.salary}")

    #     if vacancy1 >= vacancy2:
    #         print(f"Вакансия №1 {vacancy1.name_vacancy} с зарплатой {vacancy1.salary} больше вакансии №2 {vacancy2.name_vacancy} с зарплатой {vacancy2.salary}")
    #     else:
    #         print(f"Вакансия №2 {vacancy2.name_vacancy} с зарплатой {vacancy2.salary} больше вакансии №1 {vacancy1.name_vacancy} с зарплатой {vacancy1.salary}")
    #
    # else:
    #
    #     print("Недостаточно данных для сравнения")


