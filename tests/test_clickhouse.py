import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.clickhouse_client import get_clickhouse_client


def test_connection():
    """Тестирует подключение к существующей базе"""
    try:
        client = get_clickhouse_client()
        
        # Простой тестовый запрос
        result = client.query("SELECT version() as version")
        version = result.result_set[0][0]
        
        print("ClickHouse подключение успешно!")
        print(f"Версия ClickHouse: {version}")
        
        # Проверяем что база существует и доступна
        result = client.query("SHOW DATABASES")
        databases = [db[0] for db in result.result_set]
        print(f"Доступные базы: {databases}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


def main():
    print("=" * 50)
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К СУЩЕСТВУЮЩЕЙ БАЗЕ")
    print("=" * 50)
    
    if test_connection():
        print(f"\n ПОДКЛЮЧЕНИЕ РАБОТАЕТ!")
    else:
        print(f"\n ОШИБКА ПОДКЛЮЧЕНИЯ")

if __name__ == "__main__":
    main()
