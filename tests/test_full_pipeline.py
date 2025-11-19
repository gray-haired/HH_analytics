import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.data_loader import test_simple_insert, test_data_loading

if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ ПОЛНОГО ПАЙПЛАЙНА: ПАРСЕР → CLICKHOUSE")
    print("=" * 60)
    
    print(f"\n 1. Тестируем простую вставку...")
    simple_success = test_simple_insert()
    
    if simple_success:
        print(f"\n 2. Тестируем полный пайплайн...")
        full_success = test_data_loading() 
    else:
        print(f"\n Пропускаем полный тест из-за ошибки вставки")
        full_success = False
    
    if full_success:
        print(f"\n ПОЛНЫЙ ПАЙПЛАЙН РАБОТАЕТ УСПЕШНО!")
    else:
        print(f"\n ПАЙПЛАЙН НЕ СРАБОТАЛ")
