import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.parser.hh_parser import parse_vacancies

if __name__ == "__main__":
    # Тестовые запросы
    queries = ["Data Scientist", "Python developer"]
    
    results = parse_vacancies(queries, max_vacancies=5)
    
    if results:
        print(f"\nПример вакансии:")
        import json
        print(json.dumps(results[0], indent=2, ensure_ascii=False))
