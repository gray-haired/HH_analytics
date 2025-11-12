# Модель данных

## ETL Process
```python
# Основные этапы обработки
1. Extract: HH API → Raw JSON
2. Transform: Cleaning → Enrichment → Validation  
3. Load: ClickHouse ← Pandas DataFrame
```

### Data Quality
- Валидация форматов зарплат
- Дедупликация по ID вакансий
- Контроль целостности связей