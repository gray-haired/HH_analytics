import requests
import time
import json
from datetime import datetime

from .config import get_headers, REQUESTS_DELAY, TIMEOUT, MAX_PAGES


def fetch_vacancies_list(search_query: str, area: int = 113, per_page: int = 50):
    """Получает список вакансий с пагинацией"""
    
    all_vacancies = []
    headers = get_headers()
    
    for page in range(MAX_PAGES):
        print(f"Страница {page + 1}...")
        
        params = {
            "text": search_query,
            "area": area,
            "per_page": per_page,
            "page": page
        }
        
        try:
            response = requests.get(
                "https://api.hh.ru/vacancies", 
                params=params, 
                headers=headers, 
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                vacancies_on_page = len(data.get('items', []))
                print(f"Найдено: {vacancies_on_page} вакансий")
                all_vacancies.extend(data['items'])
                
                # Проверяем последнюю страницу
                if page >= data.get('pages', 1) - 1:
                    print("Последняя страница достигнута")
                    break
            else:
                print(f"Ошибка: {response.status_code}")
                break
                
        except Exception as e:
            print(f"Ошибка: {e}")
            break
    
    print(f"Всего собрано: {len(all_vacancies)} вакансий")
    return all_vacancies


def fetch_vacancy_details(vacancy_id: str):
    """Получает детальную информацию по вакансии"""
    
    headers = get_headers()
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    
    try:
        time.sleep(REQUESTS_DELAY)  # Соблюдаем лимиты API
        
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"Вакансия {vacancy_id} не найдена")
        else:
            print(f"Ошибка {response.status_code} для {vacancy_id}")
            
    except Exception as e:
        print(f"Ошибка для {vacancy_id}: {e}")
    
    return None


def parse_vacancies(search_queries, max_vacancies: int = 100):
    """Основная функция парсинга"""
    
    all_processed_vacancies = []
    
    for query in search_queries:
        print(f"\nПоиск: '{query}'")
        print("=" * 40)
        
        vacancies_list = fetch_vacancies_list(query)
        
        for i, vacancy in enumerate(vacancies_list[:max_vacancies]):
            print(f"{i+1}. {vacancy['name']}")
            
            details = fetch_vacancy_details(vacancy['id'])
            
            if details:
                # исправление: приоритет salary_range -> salary
                salary_data = details.get('salary') or {}
                salary_range_data = details.get('salary_range') or {}
                
                salary_from = salary_range_data.get('from') or salary_data.get('from')
                salary_to = salary_range_data.get('to') or salary_data.get('to')
                salary_currency = salary_range_data.get('currency') or salary_data.get('currency', '')

                # Обрабатываем данные
                processed = {
                    'id': details.get('id'),
                    'name': details.get('name'),
                    'salary_from': salary_from,
                    'salary_to': salary_to,
                    'salary_currency': salary_currency,
                    'employer': details.get('employer', {}).get('name'),
                    'area': details.get('area', {}).get('name'),
                    'experience': details.get('experience', {}).get('name'),
                    'key_skills': [skill['name'] for skill in details.get('key_skills', [])],
                    'published_at': details.get('published_at'),
                    'query': query
                }
                all_processed_vacancies.append(processed)
                
                # Логируем зарплату если есть
                if salary_from or salary_to:
                    print(f"Зарплата: {salary_from or '?'}-{salary_to or '?'} {salary_currency}")
                else:
                    print(f"Навыков: {len(processed['key_skills'])}")
    
    print(f"\nИТОГО обработано: {len(all_processed_vacancies)} вакансий")
    return all_processed_vacancies
    
