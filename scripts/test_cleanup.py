import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.cleanup import cleanup_old_data, get_database_stats, optimize_table


def main():
    print("=" * 60)
    print("ТЕСТИРУЕМ ОЧИСТКУ СТАРЫХ ДАННЫХ")
    print("=" * 60)
    
    # Статистика до очистки
    print(f"\n1. Текущая статистика:")
    stats_before = get_database_stats()
    
    # Очищаем данные старше 7 дней (для теста)
    print(f"\n2. Очистка данных старше 7 дней...")
    cleanup_old_data(days_to_keep=7)
    
    # Статистика после очистки
    print(f"\n3. Статистика после очистки:")
    stats_after = get_database_stats()
    
    # Оптимизация
    print(f"\n4. Оптимизация таблицы...")
    optimize_table()
    
    print(f"\nОЧИСТКА ЗАВЕРШЕНА")

if __name__ == "__main__":
    main()

