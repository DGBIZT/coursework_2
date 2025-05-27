import requests
from abc import ABC, abstractmethod

class VacancyApi(ABC):

    @abstractmethod
    def load_vacancies(self, keyword):
        pass


class HH(VacancyApi):
    """
    Класс для работы с API HeadHunter
    Класс Parser является родительским классом, который вам необходимо реализовать
    """

    def __init__(self):
        """Класс для парсинга данных с hh.ru"""
        self.__url = 'https://api.hh.ru/vacancies'
        self.__headers = {'User-Agent': 'HH-User-Agent'}
        self.__params = {'text': '', 'page': 0, 'per_page': 10, "area": "113"}
        self.__vacancies = []

    def load_vacancies(self, keyword):
        self.__params['text'] = keyword.lower()
        while self.__params.get('page') != 1: # Пока не достиг одной страницы
            response = requests.get(self.__url, headers=self.__headers, params=self.__params)
            if response.status_code == 200:
                vacancies = response.json()['items']
                self.__vacancies.extend(vacancies)
                self.__params['page'] += 1
            else:
                raise Exception(f"Ошибка при запросе к API: {response.status_code}")

    def get_vacancies(self):
        return self.__vacancies

class Vacancy:
    def __init__(self, name_vacancy, url_vacancy, salary, town, snippet):
        self.name_vacancy = name_vacancy.get("name")
        self.url_vacancy = url_vacancy.get('alternate_url')
        self.salary = salary.get('from') if salary else "Зарплата не указана"
        self.town = town.get('name')
        self.snippet = snippet.get("snippet").get('requirement')

    def __str__(self):
        return f"{self.name_vacancy} {self.url_vacancy} {self.salary} {self.town} {self.snippet}"

    def __eq__(self, other):
        if isinstance(other, Vacancy):
            return self.salary == other.salary
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other,Vacancy):
            return self.salary >= other.salary
        return NotImplemented


if __name__ == '__main__':
    hh_parser = HH()
    hh_parser.load_vacancies('водитель')
    vacancies_list = hh_parser.get_vacancies()

    for vacancy in vacancies_list:
        new_vacancy = Vacancy(
            name_vacancy=vacancy,
            url_vacancy=vacancy,
            salary=vacancy.get('salary'),
            town=vacancy.get('area'),
            snippet=vacancy
        )

    if len(vacancies_list) >= 2:
        vacancy1_data = vacancies_list[0]
        vacancy2_data = vacancies_list[1]

        vacancy1 = Vacancy(
            name_vacancy=vacancy1_data,
            url_vacancy=vacancy1_data,
            salary=vacancy1_data.get('salary'),
            town=vacancy1_data.get('area'),
            snippet=vacancy1_data
        )
        vacancy2 = Vacancy(
            name_vacancy=vacancy2_data,
            url_vacancy=vacancy2_data,
            salary=vacancy2_data.get('salary'),
            town=vacancy2_data.get('area'),
            snippet=vacancy2_data
        )

        if vacancy1 == vacancy2:
            print("Зарплаты равны")
        else:
            print(f"Зарплаты отличаются:{"\n"} {vacancy1.name_vacancy}{vacancy1.salary}{"\n"} {vacancy2.name_vacancy} {vacancy2.salary}")

        if vacancy1 >= vacancy2:
            print(f"Вакансия №1 {vacancy1.name_vacancy} зарплата {vacancy1.salary} больше вакансии {vacancy2.name_vacancy} с зарплатой {vacancy2.salary}")
        else:
            print(f"Вакансия №1 {vacancy2.name_vacancy} зарплата {vacancy2.salary} больше вакансии {vacancy1.name_vacancy} с зарплатой {vacancy1.salary}")
    else:

        print("Недостаточно данных для сравнения")

        # print(new_vacancy)
        # print("-" * 50)

    # print(vacancies_list)

