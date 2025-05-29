from src.utils import HH
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
    vacancies_list = hh_api.get_vacancies()
    hh_api.file_writer_base()
    top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    # filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
    # salary_range = input("Введите диапазон зарплат: ")  # Пример: 100000 - 150000

    return vacancies_list

print(user_interaction())