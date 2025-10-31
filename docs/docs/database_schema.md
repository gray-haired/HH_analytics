# Схема базы данных ClickHouse

## Таблица `vacancies`

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `id` | String | Уникальный ID вакансии | "127060619" |
| `name` | String | Название вакансии | "Data Scientist" |
| `salary_from` | Nullable(Int32) | Минимальная зарплата | 111000 |
| `salary_to` | Nullable(Int32) | Максимальная зарплата | 167000 |
| `salary_currency` | String | Валюта зарплаты | "RUR" |
| `employer_name` | String | Компания | "Яндекс" |
| `area_name` | String | Город/регион | "Москва" |
| `experience` | String | Требуемый опыт | "От 1 года до 3 лет" |
| `key_skills` | Array(String) | Массив навыков | ['Python', 'SQL'] |
| `search_query` | String | Поисковый запрос | "Data Scientist" |
| `published_at` | DateTime | Дата публикации | "2025-10-28T13:31:46+0300" |
| `created_date` | Date | Дата для партиционирования | Автоматически |

## SQL для создания таблицы

```
CREATE TABLE vacancies
(
    id String,
    name String,
    salary_from Nullable(Int32),
    salary_to Nullable(Int32),
    salary_currency String,
    employer_name String,
    area_name String,
    experience String,
    key_skills Array(String),
    search_query String,
    published_at DateTime,
    created_date Date DEFAULT toDate(published_at)
)
ENGINE = MergeTree()
PRIMARY KEY (created_date, area_name, experience)
ORDER BY (created_date, area_name, experience, id)
PARTITION BY toYYYYMM(created_date);
```

## Структура индексов

- **PRIMARY KEY**: `(created_date, area_name, experience)` - для аналитических запросов
- **ORDER BY**: `(created_date, area_name, experience, id)` - порядок хранения данных
- **PARTITION BY**: `toYYYYMM(created_date)` - партиции по месяцам

## Оптимизация под аналитику

Схема оптимизирована для типичных запросов аналитической платформы:
- Тренды по времени
- Географическое распределение  
- Статистика по опыту работы

## История изменений

### Версия 1.1 (2025-10-29)
**Добавлены новые поля:**
- `employment` (String) - тип занятости
- `schedule` (String) - график работы  
- `professional_roles` (Array(String)) - профессиональные роли

**SQL для обновления:**
```sql
ALTER TABLE vacancies 
ADD COLUMN employment String,
ADD COLUMN schedule String,
ADD COLUMN professional_roles Array(String);
```

### Версия 1.2 (2025-10-31) - Дедупликация
**Решена проблема дубликатов:**
- Таблица пересоздана с движком `ReplacingMergeTree(published_at)`
- Данные автоматически дедуплицируются по полю `id`
- Добавлена логика дедупликации на стороне приложения

**SQL миграция:**
```sql
-- Создание таблицы с дедупликацией
CREATE TABLE vacancies (...) ENGINE = ReplacingMergeTree(published_at)...;

-- Перенос данных с оконными функциями
INSERT INTO new_table 
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY id ORDER BY published_at DESC) as rn
    FROM old_table
) WHERE rn = 1;
```
Примечание: ReplacingMergeTree выполняет дедупликацию фоново, для немедленной дедупликации используйте OPTIMIZE TABLE FINAL DEDUPLICATE.
