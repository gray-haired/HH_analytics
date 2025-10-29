import os
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()


def get_clickhouse_client():
    """Создает подключение к ClickHouse Cloud через переменные окружения"""
    
    # Получаем данные из .env
    host = os.getenv('CLICKHOUSE_HOST')
    user = os.getenv('CLICKHOUSE_USER')
    password = os.getenv('CLICKHOUSE_PASSWORD')
    database = os.getenv('CLICKHOUSE_DB')
    
    if not all([host, user, password]):
        raise ValueError("Не установлены переменные окружения для ClickHouse")
    
    client = clickhouse_connect.get_client(
        host=host,
        user=user,
        password=password,
        database=database,
        secure=True
    )
    return client

