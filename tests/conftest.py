import pytest

from src.utils import HH


# Фикстура для создания тестового экземпляра класса
@pytest.fixture
def api():
    # Здесь должен быть ваш класс, который реализует метод get_vacancies()
    return HH()


# def file_writer_base(self):
@pytest.fixture
def temp_data_dir(tmp_path):
    # Создаем временную директорию для тестов
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


# @pytest.fixture
# def temp_data_dir():
#     # Создаем временную директорию
#     temp_dir = tempfile.mkdtemp()
#     try:
#         yield Path(temp_dir)
#     finally:
#         # Удаляем временную директорию после теста
#         shutil.rmtree(temp_dir)


@pytest.fixture
def mock_data_path(monkeypatch, temp_data_dir):
    # Заменяем путь к директории на временную директорию
    monkeypatch.setattr("pathlib.Path", lambda: temp_data_dir)
    # Создаем директорию data в временной директории
    (temp_data_dir / "data").mkdir()
