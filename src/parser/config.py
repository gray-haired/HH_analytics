import os
from dotenv import load_dotenv


load_dotenv()

# Настройки HH API
USER_AGENT_NAME = os.getenv("HH_USER_AGENT_NAME", "HH-Analytics-Platform")
USER_AGENT_EMAIL = os.getenv("HH_USER_AGENT_EMAIL", "")

# Параметры запросов
REQUESTS_DELAY = float(os.getenv("HH_REQUESTS_DELAY", "0.3"))
TIMEOUT = int(os.getenv("HH_TIMEOUT", "10"))
MAX_PAGES = int(os.getenv("HH_MAX_PAGES", "20"))

def get_headers():
    """Возвращает headers для HH API"""
    if USER_AGENT_EMAIL:
        return {"User-Agent": f"{USER_AGENT_NAME} ({USER_AGENT_EMAIL})"}
    else:
        return {"User-Agent": USER_AGENT_NAME}

# Проверяем конфигурацию
if not USER_AGENT_EMAIL:
    print("Внимание: HH_USER_AGENT_EMAIL не установлен")
    
