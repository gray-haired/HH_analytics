import os
import sys
# Добавляем корневую директорию проекта в sys.path, чтобы можно было импортировать модули из src
# __file__ - это путь к app.py
# os.path.dirname(__file__) - это путь к dashboard/
# os.path.abspath(...) - это абсолютный путь
# os.path.join(..., '..') - это путь к корневой папке HH_analytics/
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

import pytest

from src.analytics.data_service import load_vacancies_data

def test_load_vacancies_data_returns_dataframe(mocker):
    """Проверяет, что функция загрузки данных возвращает DataFrame."""
    # Здесь будет код для мокирования клиента ClickHouse
    # и проверки, что load_vacancies_data возвращает pd.DataFrame
    assert True # Заглушка
    