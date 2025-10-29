import json
from datetime import datetime
from .clickhouse_client import get_clickhouse_client
from .cleanup import cleanup_old_data, get_database_stats, optimize_table


def prepare_vacancy_data(vacancy):
    """Подготавливает данные вакансии для вставки в ClickHouse"""
    
    # Обрабатываем зарплату (может быть None)
    salary = vacancy.get('salary') or {}
    
    # Преобразуем дату публикации
    published_at = vacancy.get('published_at')
    if published_at:
        try:
            published_at = published_at.replace('+0300', '').replace('+00:00', '')
            published_at = datetime.fromisoformat(published_at)
        except Exception:
            published_at = datetime.now()
    else:
        published_at = datetime.now()
    
    # created_date автоматически вычисляется из published_at
    created_date = published_at.date()
    
    # 12 столбцов
    return [
        vacancy.get('id', ''),                     # id
        vacancy.get('name', ''),                   # name
        salary.get('from'),                        # salary_from
        salary.get('to'),                          # salary_to
        salary.get('currency', ''),                # salary_currency
        vacancy.get('employer', ''),               # employer_name
        vacancy.get('area', ''),                   # area_name
        vacancy.get('experience', ''),             # experience
        vacancy.get('key_skills', []),             # key_skills
        vacancy.get('query', ''),                  # search_query
        published_at,                              # published_at
        created_date                               # created_date
    ]


def insert_vacancies_to_clickhouse(vacancies):
    """Загружает список вакансий в ClickHouse"""
    
    if not vacancies:
        print("Нет данных для загрузки")
        return False
    
    try:
        print("Подключаемся к ClickHouse...")
        client = get_clickhouse_client()
        
        # Подготавливаем данные
        print(f"Подготавливаем {len(vacancies)} вакансий...")
        prepared_data = [prepare_vacancy_data(vac) for vac in vacancies]
        
        # Выполняем вставку
        print("Загружаем данные в ClickHouse...")
        client.insert(table='vacancies', data=prepared_data)
        
        print(f"Успешно загружено {len(vacancies)} вакансий в ClickHouse")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки в ClickHouse: {e}")
        import traceback
        traceback.print_exc()
        return False


def insert_vacancies_with_cleanup(vacancies, days_to_keep=90):
    """Загружает данные и очищает старые записи"""
    
    success = insert_vacancies_to_clickhouse(vacancies)
    
    if success:
        print("\n" + "="*50)
        print("УПРАВЛЕНИЕ ДАННЫМИ")
        print("="*50)
        
        # Показываем статистику до очистки
        print("ДО очистки:")
        get_database_stats()
        
        # Очищаем старые данные
        cleanup_old_data(days_to_keep=days_to_keep)
        
        # Показываем статистику после очистки
        print(f"\n ПОСЛЕ очистки:")
        get_database_stats()
        
        # Оптимизируем таблицу
        optimize_table()
    
    return success


def test_simple_insert():
    """Простой тест вставки"""
    
    try:
        client = get_clickhouse_client()
        
        now = datetime.now()
        
        # 12 столбцов - как в таблице
        test_data = [[
            'test_001',                    # id
            'Test Vacancy',                # name
            100000,                        # salary_from
            150000,                        # salary_to
            'RUR',                         # salary_currency
            'Test Company',                # employer_name
            'Москва',                      # area_name
            'Нет опыта',                   # experience
            ['Python', 'SQL'],             # key_skills
            'Test',                        # search_query
            now,                           # published_at
            now.date()                     # created_date
        ]]
        
        client.insert(table='vacancies', data=test_data)
        print("Простой тест вставки прошел успешно!")
        return True
        
    except Exception as e:
        print(f"Простой тест не прошел: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_loading():
    """Тестирует полный пайплайн: парсинг → загрузка"""
    
    from src.parser.hh_parser import parse_vacancies
    
    print("Тестируем полный ETL-пайплайн...")
    
    # Парсим тестовые данные
    test_queries = ["Data Scientist"]
    vacancies = parse_vacancies(test_queries, max_vacancies=2)  # Уменьшили для теста
    
    if vacancies:
        # Загружаем в ClickHouse
        success = insert_vacancies_to_clickhouse(vacancies)
        
        if success:
            # Проверяем что данные загрузились
            client = get_clickhouse_client()
            result = client.query("SELECT COUNT(*) FROM vacancies")
            count = result.result_set[0][0]
            print(f"Всего вакансий в базе: {count}")
            
        return success
    else:
        print("Не удалось получить данные для теста")
        return False

