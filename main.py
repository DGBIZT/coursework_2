from src.utils import HH, Vacancy
hh_api = HH()

# vacancies_list = hh_api.get_vacancies()
# hh_api.file_writer_base()
# print(vacancies_list)

def filtered_vacancies(vacancies_list, filter_words):
    pass

def user_interaction():
    platforms = ["HeadHunter"]
    search_query = input("Введите поисковый запрос: ")
    hh_api._VacancyApi__load_vacancies(search_query)
    vacancies_data = hh_api.get_vacancies()
    hh_api.file_writer_base()
    top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    sort_up_down = input("Фильтровать по убыванию или по возрастанию:  ")

    # filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
    # salary_range = input("Введите диапазон зарплат: ")  # Пример: 100000 - 150000

    vacancies_list = []
    for vacancy in vacancies_data:
        new_vacancy = Vacancy(vacancy)  # Передаем всю вакансию как один параметр
        vacancies_list.append(new_vacancy)

    # Сортируем список по зарплате
    sorted_vacancies = sorted(vacancies_list, key=lambda v: v.salary, reverse=True)

    # Выводим отсортированные вакансии
    for vacancy in sorted_vacancies:
        print(vacancy)
        print("-" * 50)  # Разделитель между вакансиями
    return vacancies_list

print(user_interaction())