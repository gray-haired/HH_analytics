# HH Analytics Platform

Реальная аналитическая система для мониторинга рынка труда IT-специалистов. Проект демонстрирует полный цикл ETL: от сбора данных с HH.ru до визуализации в BI-инструментах.

## Особенности

- **Ежедневный мониторинг** ключевых IT-вакансий (Data Scientist, Data Analyst, etc.)
- **Автоматизированный ETL-пайплайн** с обработкой ошибок и дедупликацией
- **Cloud-архитектура** с использованием ClickHouse Cloud для хранения данных
- **Безопасная конфигурация** через environment variables
- **Готовность к промышленной эксплуатации** с CI/CD через GitHub Actions

## Технологический стек

| Компонент | Технология |
|-----------|------------|
| **Парсинг** | Python, HH API, requests |
| **База данных** | ClickHouse Cloud, ReplacingMergeTree |
| **Автоматизация** | GitHub Actions, cron-расписание |
| **Безопасность** | Environment variables, GitHub Secrets |
| **Мониторинг** | Встроенная статистика и логирование |

## Архитектура
Парсер HH API → ETL-обработка → ClickHouse Cloud → BI-дашборды ↑ ↓ GitHub Actions (00:01 МСК) Power BI / Tableau


## Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/hh-analytics-platform.git
cd hh-analytics-platform
```
### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```
### 3. Настройка окружения
```bash
cp .env.example .env
```
### 4. Настройка ClickHouse Cloud
 - Создайте аккаунт на console.clickhouse.cloud
 - Создайте базу данных hh_analytics
 - Выполните SQL из docs/database_schema.md для создания таблиц
 - Добавьте данные подключения в .env файл
  
### 5. Запуск тестов
```bash
# Тест парсера
python scripts/test_parser.py

# Тест подключения к БД
python scripts/test_clickhouse.py

# Полный ETL-пайплайн
python scripts/test_full_pipeline.py
```

## База данных
### Структура
Таблица vacancies содержит 15 полей, включая информацию о вакансиях, зарплатах, навыках и метаданных.

### Миграции
При изменении структуры базы:

- Выполните ALTER TABLE в ClickHouse консоли
- Обновите код в src/database/data_loader.py
- Задокументируйте изменения в docs/database_schema.md

### Версии
v1.2: Дедупликация через ReplacingMergeTree
v1.1: Добавлены поля employment, schedule, professional_roles
v1.0: Первоначальная структура с 12 полями

## Автоматизация

Проект использует GitHub Actions для ежедневного запуска в 00:01 по Москве. Workflow включает:

- Автоматический парсинг новых вакансий
- Загрузку в ClickHouse Cloud
- Очистку старых данных (90+ дней)
- Оповещения об успехе/ошибках

## BI-визуализация (в разработке)