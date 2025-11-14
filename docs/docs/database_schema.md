# База данных ClickHouse

## Обзор схемы данных

Система использует **ClickHouse Cloud** — высокопроизводительную колоночную СУБД, оптимизированную для аналитических рабочих нагрузок. Схема спроектирована для эффективных запросов агрегации и временных рядов.

## Структура таблицы `vacancies`

| Поле | Тип | Описание | Особенности |
|------|-----|----------|-------------|
| `id` | `String` | Уникальный идентификатор вакансии | Primary key, из HH API |
| `name` | `String` | Название позиции | Полное наименование |
| `salary_from` | `Nullable(Int32)` | Нижняя граница вилки | Только RUR, проверка на 10к-1млн |
| `salary_to` | `Nullable(Int32)` | Верхняя граница вилки | Опциональное поле |
| `salary_currency` | `String` | Валюта зарплаты | Фильтрация только RUR |
| `employer_name` | `String` | Наименование компании | Нормализованные названия |
| `area_name` | `String` | Локация | Город/регион РФ |
| `experience` | `String` | Требуемый опыт | "Junior/Middle/Senior" |
| `key_skills` | `Array(String)` | Ключевые навыки | Массив технологий |
| `search_query` | `String` | Исходный запрос | Для анализа покрытия |
| `published_at` | `DateTime` | Время публикации | ISO format с таймзоной |
| `created_date` | `Date` | Дата для партиций | Автогенерация из published_at |

## DDL таблицы

```sql
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
ENGINE = ReplacingMergeTree(published_at)
PARTITION BY toYYYYMM(created_date)
ORDER BY (created_date, area_name, experience, id);
```
## Стратегия индексирования
### Первичный ключ
```sql
PRIMARY KEY (created_date, area_name, experience)
```
- created_date — быстрый доступ по временным диапазонам
- area_name — оптимизация географических запросов
- experience — фильтрация по уровню опыта

### Сортировка данных
```sql
ORDER BY (created_date, area_name, experience, id)
```
Порядок хранения на диске соответствует частым паттернам запросов.

### Партиционирование
```sql
PARTITION BY toYYYYMM(created_date)
```
- Ежемесячные партиции для эффективного DROP старых данных
- Автоматическое управление временными интервалами

## Оптимизация запросов

### Типичные аналитические запросы
```sql
-- тренды по времени (использует created_date first)
SELECT created_date, COUNT(*) 
FROM vacancies 
WHERE created_date >= '2024-01-01'
GROUP BY created_date;

-- ееографическое распределение (area_name в PK)
SELECT area_name, COUNT(*) 
FROM vacancies 
WHERE created_date >= today() - 30
GROUP BY area_name;

-- анализ по опыту (experience в PK)
SELECT experience, COUNT(*)
FROM vacancies
WHERE created_date = today()
GROUP BY experience;
```

## Миграции схемы

Версия 1.1 — Расширение полей
```sql
ALTER TABLE vacancies 
ADD COLUMN employment String,
ADD COLUMN schedule String,
ADD COLUMN professional_roles Array(String);
```

Версия 1.2 — Дедупликация
```sql
-- миграция на ReplacingMergeTree
CREATE TABLE vacancies_new (...) 
ENGINE = ReplacingMergeTree(published_at)...;

INSERT INTO vacancies_new 
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY id ORDER BY published_at DESC) as rn
    FROM vacancies_old
) WHERE rn = 1;
```

## Мониторинг
```sql
-- анализ использования индексов
SELECT table, primary_key_bytes_in_memory
FROM system.parts 
WHERE table = 'vacancies';
```

