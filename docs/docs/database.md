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

## Структура индексов

- **PRIMARY KEY**: `(created_date, area_name, experience)` - для аналитических запросов
- **ORDER BY**: `(created_date, area_name, experience, id)` - порядок хранения данных
- **PARTITION BY**: `toYYYYMM(created_date)` - партиции по месяцам

## Оптимизация под аналитику

Схема оптимизирована для типичных запросов аналитической платформы:
- Тренды по времени
- Географическое распределение  
- Статистика по опыту работы
