# Деплой и инфраструктура

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: Daily ETL Pipeline
on:
  schedule:
    - cron: '0 21 * * *'  # 00:01 MSK
```

### Cloud Infrastructure
- ClickHouse Cloud: Managed кластер в Germany West
- Streamlit Cloud: Бесплатный хостинг дашбордов
- GitHub Actions: Автоматизация пайплайнов

### Мониторинг и логирование
- Автоматические уведомления о сбоях
- Логи выполнения в GitHub Actions
- Метрики производительности

