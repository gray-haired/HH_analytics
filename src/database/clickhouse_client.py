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
    
    # проверка, что все необходимые переменные установлены
    missing_vars  = []
    if not host: missing_vars.append('CLICKHOUSE_HOST')
    if not user: missing_vars .append('CLICKHOUSE_USER')
    if not password: missing_vars .append('CLICKHOUSE_PASSWORD')
    if not database: missing_vars .append('CLICKHOUSE_DB')
    
    if missing_vars:
        error_msg = f"Не установлены переменные окружения: {', '.join(missing_vars)}"
        print(f"{error_msg}")
        raise ValueError(error_msg)
    
    try:    
        client = clickhouse_connect.get_client(
            host=host,
            user=user,
            password=password,
            database=database,
            secure=True
        )
        return client
    
    except Exception as e:
        print(f"Ошибка подключения к ClickHouse: {e}")
        raise
