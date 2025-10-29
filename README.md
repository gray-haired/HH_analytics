# HH Analytics Platform

Реальная аналитическая система для мониторинга рынка труда IT-специалистов.

## Архитектура проекта

- **Парсер HH API** → сбор данных о вакансиях
- **ETL-пайплайн** → обработка и загрузка в ClickHouse
- **BI-дашборды** → визуализация метрик
- **Автоматизация** → GitHub Actions + расписание

## Быстрый старт

```bash
git clone <repository>
cd hh-analytics-platform
pip install -r requirements.txt

## Настройка ClickHouse Cloud

1. Создайте базу на [console.clickhouse.cloud](https://console.clickhouse.cloud)
2. Скопируйте пример конфигурации:
```bash
cp .env.example .env