import pytest
import json
import os
import requests
from src.utils import VacancyApi
from src.utils import HH
from src.utils import Vacancy
from unittest.mock import patch, Mock
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

def test_abstract_methods():
    """
    Проверяем, что методы действительно абстрактные
    """
    with pytest.raises(TypeError):
        VacancyApi()  # Не может быть создан экземпляр абстрактного класса


def test_missing_implementation():
    """
    Проверяем, что невозможно создать подкласс без реализации всех методов
    """

    class IncompleteVacancyApi(VacancyApi):
        def file_writer_base(self):
            return "Writing to file"

    with pytest.raises(TypeError):
        IncompleteVacancyApi()  # Должна возникнуть ошибка, так как не реализован __load_vacancies

# Базовый тест инициализации class HH(VacancyApi):  def __init__(self):
def test_hh_init():
 hh = HH()
 assert hh._HH__url == 'https://api.hh.ru/vacancies'
 assert hh._HH__headers == {'User-Agent': 'HH-User-Agent'}
 assert hh._HH__params == {'text': '', 'page': 0, 'per_page': 100, "area": "113"}
 assert hh._HH__vacancies == []


# тестирование метода def _VacancyApi__load_vacancies(self, keyword):
# Тест базовой загрузки вакансий
@patch('requests.get')
def test_load_vacancies(mock_get):
    # Создаем тестовый ответ
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"id": 1, "name": "Python Developer"},
            {"id": 2, "name": "Junior Python Developer"}
        ],
        "pages": 1
    }
    mock_get.return_value = mock_response

    hh = HH()
    hh._VacancyApi__load_vacancies("Python")

    assert mock_get.called
    assert mock_get.call_args[0][0] == 'https://api.hh.ru/vacancies'
    assert mock_get.call_args[1]['params']['text'] == 'python'
    assert len(hh._HH__vacancies) == 2
    assert hh._HH__vacancies[0]['name'] == 'Python Developer'
    assert hh._HH__vacancies[1]['name'] == 'Junior Python Developer'

# Тест обработки ошибки API
@patch('requests.get')
def test_load_vacancies_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    hh = HH()
    with pytest.raises(Exception, match="Ошибка при запросе к API: 500"):
        hh._VacancyApi__load_vacancies("Python")


# Тест загрузки всех 20 страниц
@patch('requests.get')
def test_load_all_pages(mock_get):
    # Создаем 20 разных ответов
    responses = []
    for i in range(20):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"id": i, "name": f"Python Developer {i}"}],
            "pages": 20
        }
        responses.append(mock_response)

    mock_get.side_effect = responses

    hh = HH()
    hh._VacancyApi__load_vacancies("Python")

    assert len(mock_get.call_args_list) == 20
    assert len(hh._HH__vacancies) == 20
    assert hh._HH__vacancies[0]['name'] == 'Python Developer 0'
    assert hh._HH__vacancies[19]['name'] == 'Python Developer 19'


# Тест с пустыми страницами
@patch('requests.get')
def test_empty_pages(mock_get):
    # Первый ответ с вакансиями
    mock_response1 = Mock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = {
        "items": [{"id": 1, "name": "Python Developer"}],
        "pages": 20
    }

    # Остальные пустые
    empty_response = Mock()
    empty_response.status_code = 200
    empty_response.json.return_value = {
        "items": [],
        "pages": 20
    }

    mock_get.side_effect = [mock_response1] + [empty_response] * 19

    hh = HH()
    hh._VacancyApi__load_vacancies("Python")

    assert len(mock_get.call_args_list) == 20
    assert len(hh._HH__vacancies) == 1
    assert hh._HH__vacancies[0]['name'] == 'Python Developer'


# Тест с некорректным ответом
@patch('requests.get')
def test_invalid_response(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}  # Пустой ответ
    mock_get.return_value


# Тест проверки типа возвращаемого значения для метода def get_vacancies(self):
def test_get_vacancies_returns_list(api):
    """
    Проверяем, что метод возвращает список
    """
    vacancies = api.get_vacancies()
    assert isinstance(vacancies, list)

# Тест проверки пустого списка
def test_get_vacancies_empty_list(api):
    """
    Проверяем поведение при пустом списке вакансий
    """
    assert api.get_vacancies() == []

#def file_writer_base(self):
def test_file_writer_base():
    # Создаем тестовый экземпляр класса
    test_instance = HH()
    test_instance._HH__vacancies = [{"test": "data"}]

    # Запускаем метод записи
    test_instance.file_writer_base()

    # Проверяем существование файла
    file_path = "data/vacancies.json"
    assert os.path.exists(file_path)

    # Проверяем содержимое файла
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == [{"test": "data"}]


def test_file_writer_base_success(mock_data_path):
    # Тестируем успешную запись
    test_instance = HH()
    test_instance._HH__vacancies = {"test": "data"}

    # Запускаем метод записи
    test_instance.file_writer_base()

    # Проверяем существование файла
    file_path = Path('data/vacancies.json')
    assert file_path.exists()

    # Проверяем содержимое файла
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == {"test": "data"}


def test_file_writer_base_empty_data(mock_data_path):
    # Тестируем запись пустого словаря
    test_instance = HH()
    test_instance._HH__vacancies = {}

    test_instance.file_writer_base()

    file_path = Path('data/vacancies.json')
    assert file_path.exists()
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == {}



# class Vacancy:   def __init__(self, data):
def test_vacancy_init_full_data():
    data = {
        'name': 'Python Developer',
        'alternate_url': 'https://example.com',
        'salary': {'from': 100000},
        'area': {'name': 'Москва'},
        'snippet': {'requirement': 'Опыт от 3 лет'}
    }
    vacancy = Vacancy(data)

    assert vacancy.name_vacancy == 'Python Developer'
    assert vacancy.url_vacancy == 'https://example.com'
    assert vacancy._Vacancy__salary == 100000
    assert vacancy.town == 'Москва'
    assert vacancy.snippet == 'Опыт от 3 лет'
    assert vacancy.salary == 100000  # Используем свойство вместо прямого доступа

# def __str__(self):
def test_str_full_data():
    data = {
        'name': 'Python Developer',
        'alternate_url': 'https://example.com',
        'salary': {'from': 100000},
        'area': {'name': 'Москва'},
        'snippet': {'requirement': 'Опыт от 3 лет'}
    }
    vacancy = Vacancy(data)

    expected_str = 'Python Developer https://example.com 100000 Москва Опыт от 3 лет'
    assert str(vacancy) == expected_str


# Тест на равенство зарплат def __eq__(self, other):
def test_eq_same_salary():
    data1 = {'salary': {'from': 100000}}
    data2 = {'salary': {'from': 100000}}

    vacancy1 = Vacancy(data1)
    vacancy2 = Vacancy(data2)

    assert vacancy1 == vacancy2

# Тест на сравнение с None
def test_eq_none():
    data = {'salary': {'from': 100000}}
    vacancy = Vacancy(data)

    assert vacancy != None


# Тест на сравнение с большей зарплатой def __ge__(self, other):
def test_ge_greater_salary():
    data1 = {'salary': {'from': 150000}}
    data2 = {'salary': {'from': 100000}}

    vacancy1 = Vacancy(data1)
    vacancy2 = Vacancy(data2)

    assert vacancy1 >= vacancy2
    assert not (vacancy2 >= vacancy1)

# Тест на сравнение с None
def test_ge_none():
    data = {'salary': {'from': 100000}}
    vacancy = Vacancy(data)

    with pytest.raises(TypeError):
        vacancy >= None


# Тест на полное совпадение всех ключевых слов, def matches_keywords(self, keywords):
def test_matches_keywords_all_match():
    data = {
        'name': 'Python Developer',
        'snippet': {'requirement': 'Опыт работы от 3 лет, знание Django'},
        'area': {'name': 'Москва'}
    }
    vacancy = Vacancy(data)

    keywords = ['python', 'django', 'москва']
    assert vacancy.matches_keywords(keywords) == True


# Тест на получение топ вакансий def top_number(vacancies, number):
def test_top_number_basic():
    # Создаем тестовые вакансии с разными зарплатами
    vacancies = [
        Vacancy({'salary': {'from': 150000}}),
        Vacancy({'salary': {'from': 100000}}),
        Vacancy({'salary': {'from': 200000}}),
        Vacancy({'salary': {'from': 120000}})
    ]

    # Проверяем получение топ-2 вакансий
    top = Vacancy.top_number(vacancies, 2)
    assert len(top) == 3  # Учтите, что метод возвращает number + 1
    assert top[0].salary == 150000
    assert top[1].salary == 100000
    assert top[2].salary == 200000


# Тест на базовую функциональность def salary_range(vacancies, salary_range):
def test_salary_range_basic():
    # Создаем тестовые вакансии с разными зарплатами
    vacancies = [
        Vacancy({'salary': {'from': 150000}}),
        Vacancy({'salary': {'from': 100000}}),
        Vacancy({'salary': {'from': 200000}}),
        Vacancy({'salary': {'from': 120000}}),
        Vacancy({'salary': {'from': 80000}})
    ]

    # Проверяем фильтрацию по диапазону 100000-150000
    filtered = Vacancy.salary_range(vacancies, (100000, 150000))
    assert len(filtered) == 3
    assert all(100000 <= vacancy.salary <= 150000 for vacancy in filtered)


# Тест на пустой результат
def test_salary_range_empty():
    vacancies = [
        Vacancy({'salary': {'from': 150000}}),
        Vacancy({'salary': {'from': 200000}}),
        Vacancy({'salary': {'from': 120000}})
    ]

    filtered = Vacancy.salary_range(vacancies, (1000000, 2000000))
    assert len(filtered) == 0



