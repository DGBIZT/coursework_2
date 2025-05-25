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
    def __init__(self, name_vacancy, url_vacancy, salary, town, description):
        self.name_vacancy = name_vacancy.get("name")
        self.url_vacancy = url_vacancy.get('alternate_url')
        self.salary = salary.get('from') if salary else "Зарплата не указана"
        self.town = town.get('name')
        self.description = description.get('description')

    def __str__(self):
        return (f"{self.salary}")




if __name__ == '__main__':
    # hh = HH()
    # # fgh = "vacancies.json"
    # # adf = HH(fgh)
    # hh.load_vacancies('python')
    # # all_vac = hh.get_vacancies()
    # all_vacancy = Vacancy
    # print(all_vacancy)
    # Создаем экземпляр класса HH
    hh_parser = HH()

    # Загружаем вакансии
    hh_parser.load_vacancies('водитель')

    # Получаем список вакансий
    vacancies_list = hh_parser.get_vacancies()

    # Теперь можно работать со списком вакансий
    for vacancy in vacancies_list:
        # Создаем объекты класса Vacancy с обработкой возможных None значений
        new_vacancy = Vacancy(
            name_vacancy=vacancy,
            url_vacancy=vacancy,
            salary=vacancy.get('salary'),
            town=vacancy.get('area'),
            description=vacancy
        )
        print(new_vacancy)

