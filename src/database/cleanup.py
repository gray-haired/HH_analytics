from .clickhouse_client import get_clickhouse_client
from datetime import datetime, timedelta


def cleanup_old_data(days_to_keep=90):
    """Удаляет вакансии старше указанного количества дней"""
    
    try:
        client = get_clickhouse_client()
        
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date()
        
        # считаем сколько записей будет удалено
        count_query = "SELECT COUNT(*) FROM vacancies WHERE created_date < %(cutoff_date)s"
        count_result = client.query(count_query, {'cutoff_date': cutoff_date})
        records_to_delete = count_result.result_set[0][0]
        
        if records_to_delete > 0:
            delete_query = "ALTER TABLE vacancies DELETE WHERE created_date < %(cutoff_date)s"
            client.command(delete_query, {'cutoff_date': cutoff_date})
            
            print(f"Удалено {records_to_delete} вакансий старше {cutoff_date}")
        else:
            print(f"Нет данных для удаления старше {cutoff_date}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка очистки данных: {e}")
        return False


def get_database_stats():
    """Возвращает статистику базы данных"""
    
    try:
        client = get_clickhouse_client()
        
        # Общее количество вакансий
        count_result = client.query("SELECT COUNT(*) FROM vacancies")
        total_count = count_result.result_set[0][0]
        
        # Диапазон дат
        dates_result = client.query("""
            SELECT MIN(created_date), MAX(created_date) 
            FROM vacancies
        """)
        min_date, max_date = dates_result.result_set[0]
        
        # Количество вакансий по дням (последние 7 дней)
        recent_stats = client.query("""
            SELECT created_date, COUNT(*) 
            FROM vacancies 
            WHERE created_date >= today() - 7
            GROUP BY created_date 
            ORDER BY created_date DESC
        """)
        
        print("СТАТИСТИКА БАЗЫ ДАННЫХ:")
        print(f"   Всего вакансий: {total_count}")
        print(f"   Период данных: {min_date} - {max_date}")
        
        if recent_stats.result_set:
            print("   Последние 7 дней:")
            for date, count in recent_stats.result_set:
                print(f"     {date}: {count} вакансий")
        
        return {
            'total_count': total_count,
            'min_date': min_date,
            'max_date': max_date
        }
        
    except Exception as e:
        print(f"Ошибка получения статистики: {e}")
        return None


def optimize_table():
    """Оптимизирует таблицу после удаления данных"""
    
    try:
        client = get_clickhouse_client()
        client.command("OPTIMIZE TABLE vacancies FINAL")
        print("Таблица оптимизирована")
        return True
    except Exception as e:
        print(f"Ошибка оптимизации: {e}")
        return False

