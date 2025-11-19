import streamlit as st
import clickhouse_connect
import pandas as pd

# КОНФИГУРАЦИЯ И ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ

@st.cache_resource(ttl=3600)  # кэширование подключения на 1 час
def get_clickhouse_client():
    """
    Создает и возвращает подключение к ClickHouse Cloud.
    Использует переменные окружения из Streamlit Secrets.
    """
    try:
        client = clickhouse_connect.get_client(
                                                host=st.secrets["CLICKHOUSE_HOST"],
                                                user=st.secrets["CLICKHOUSE_USER"], 
                                                password=st.secrets["CLICKHOUSE_PASSWORD"],
                                                database=st.secrets["CLICKHOUSE_DB"],
                                                secure=True
                                            )
        st.success("Подключение к ClickHouse установлено")
        return client
    except Exception as e:
        st.error(f"Ошибка подключения к ClickHouse: {e}")
        return None
    

def test_connection():
    """Проверяет подключение к базе данных"""
    client = get_clickhouse_client()
    if client:
        try:
            result = client.query("SELECT count(*) as cnt FROM vacancies")
            count = result.result_set[0][0]
            return True, count
        except Exception as e:
            return False, f"Ошибка: {e}"
    return False, "Клиент не создан"


# ЗАГРУЗКА ДАННЫХ

@st.cache_data(ttl=3600)  # кэширование данных на 1 час
def load_vacancies_data(days=90):
    """
    Загружает данные о вакансиях за указанный период.
    Возвращает DataFrame с основной информацией.
    """
    client = get_clickhouse_client()
    if not client:
        return pd.DataFrame()
    
    try:
        query = f"""
        SELECT 
              created_date as date
            , area_name as city
            , experience
            , key_skills
            , salary_from_rub as salary_from
            , salary_to_rub as salary_to
            , employer_name as company
            , search_query as query
        FROM preset_vacancies_view 
        WHERE created_date >= today() - {days}
        ORDER BY date DESC
        """
        
        result = client.query(query)
        
        # преобразование результата в DataFrame
        df = pd.DataFrame(result.result_set, 
                          columns=[
                                      'date'
                                    , 'city'
                                    , 'experience'
                                    , 'skills'
                                    , 'salary_from'
                                    , 'salary_to'
                                    , 'company'
                                    , 'query'
                                    ]
                        )
        
        # конвертирование даты в правильный формат
        df['date'] = pd.to_datetime(df['date'])
        
        return df
        
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return pd.DataFrame()
    
    # ПРАВИЛЬНЫЙ РАСЧЕТ ВАКАНСИЙ С ЗАРПЛАТОЙ
    
# выакансия считается "с зарплатой" если указан salary_from ИЛИ salary_to
def has_salary(row):
    return not pd.isna(row['salary_from']) or not pd.isna(row['salary_to'])
    
# ПРАВИЛЬНЫЙ РАСЧЕТ МЕДИАННОЙ ЗАРПЛАТЫ
    
#TODO: нужен адекватный расчет медианной зарплаты с учетом наличия salary_from и salary_to
# Для медианной зарплаты используем salary_from, когда он есть, иначе salary_to
def get_effective_salary(row):
    if not pd.isna(row['salary_from']):
        return row['salary_from']
    elif not pd.isna(row['salary_to']):
        return row['salary_to']
    else:
        return None

