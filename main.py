from src.utils import HH, Vacancy
hh_api = HH()

def user_interaction():
    vacancies_list = []
    platforms = ["HeadHunter"]
    search_query = input("Введите поисковый запрос: ")
    hh_api._VacancyApi__load_vacancies(search_query)
    vacancies_data = hh_api.get_vacancies()
    hh_api.file_writer_base()
    sort_up_down = input("Фильтровать по убыванию или по возрастанию:  ").lower()
    top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    min_salary = int(input("Введите минимальную зарплату: "))
    max_salary = int(input("Введите максимальную зарплату: "))

    # Проверяем корректность диапазона
    if min_salary > max_salary:
        raise ValueError("Минимальная зарплата не может быть больше максимальной")

    filter_words = input("Введите ключевые слова для фильтрации вакансий: ").lower().split()

    # Создаем объекты и добавляем их в список
    for vacancy in vacancies_data:
        new_vacancy = Vacancy(vacancy)  # Передаем всю вакансию как один параметр
        vacancies_list.append(new_vacancy)

    # Фильтруем вакансии
    filtered_vacancies = Vacancy.salary_range(vacancies_list, (min_salary, max_salary))

    # Сортируем список по зарплате по убыванию или возрастанию
    if sort_up_down == "убыванию":
        sorted_vacancies = sorted(filtered_vacancies, key=lambda v: v.salary, reverse=True)
    else:
        sorted_vacancies = sorted(filtered_vacancies, key=lambda v: v.salary)

    # Выводим топ N вакансий
    top_vacancies = Vacancy.top_number(sorted_vacancies, top_n)

    # Фильтруем список вакансий
    filter_vacancies = []
    for vacancy in top_vacancies:
        if vacancy.matches_keywords(filter_words):
            filter_vacancies.append(vacancy)

    # Выводим отсортированные вакансии
    for vacancy in filter_vacancies:
        print(vacancy)
        print("-" * 50)  # Разделитель между вакансиями

user_interaction()