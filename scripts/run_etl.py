#!/usr/bin/env python3
"""
Основной скрипт для ETL-пайплайна
Запускается через GitHub Actions ежедневно
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.parser.hh_parser import parse_vacancies
from src.database.data_loader import insert_vacancies_to_clickhouse
from src.database.cleanup import cleanup_old_data, get_database_stats, optimize_table


def main():
    print("=" * 60)
    print("🚀 ЗАПУСК ETL-ПАЙПЛАЙНА")
    print("=" * 60)
    
    # Поисковые запросы для мониторинга
    search_queries = [
        "Data Scientist",
        "Data Analyst", 
        "Data Engineer",
        "Machine Learning",
        "Python developer"
    ]
    
    try:
        # 1. Парсинг данных с HH
        print("Парсинг вакансий с HH API...")
        vacancies = parse_vacancies(search_queries, max_vacancies=500)  # Лимит для бесплатного тарифа
        
        if not vacancies:
            print("Не удалось получить данные с HH API")
            return False
        
        print(f"Получено {len(vacancies)} вакансий")
        
        # 2. Загрузка в ClickHouse
        print("Загрузка данных в ClickHouse...")
        success = insert_vacancies_to_clickhouse(vacancies)
        
        if not success:
            print("Ошибка загрузки в базу данных")
            return False
        
        # 3. Очистка старых данных (90 дней)
        print("Очистка старых данных...")
        cleanup_old_data(days_to_keep=90)
        
        # 4. Оптимизация таблицы
        print("Оптимизация таблицы...")
        optimize_table()
        
        # 5. Финальная статистика
        print("Финальная статистика:")
        get_database_stats()
        
        print("\nETL-ПАЙПЛАЙН УСПЕШНО ЗАВЕРШЕН!")
        return True
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

