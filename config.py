# Файл: config.py
import os
from typing import Set

# Загружаем переменные окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Если python-dotenv не установлен, используем только системные переменные
    pass

# Загрузка переменных окружения
def load_config():
    """Загружает конфигурацию из переменных окружения"""
    
    # Токен бота
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8486386170:AAEGHCYOtGlx3TrmZ3e9vQ7p8PbtCgs0YMw")
    
    # Токен платежного провайдера (временно отключен до настройки в @BotFather)
    PAYMENTS_PROVIDER_TOKEN = os.getenv("PAYMENTS_PROVIDER_TOKEN", "")
    
    # Настройки ЮMoney
    YOOMONEY_RECEIVER = os.getenv("YOOMONEY_RECEIVER", "4100118987681575")
    YOOMONEY_SECRET = os.getenv("YOOMONEY_SECRET", "SaTKEuJWPVXJI/JFpXDCHZ4q")
    YOOMONEY_NOTIFICATION_URL = os.getenv("YOOMONEY_NOTIFICATION_URL", "https://web-production-fa7dc.up.railway.app/yoomoney")
    
    # Тарифы для оплаты
    PAYMENT_PLANS = {
        "1": {"price": 50, "description": "1 публикация"},
        "5": {"price": 200, "description": "5 публикаций"},
        "10": {"price": 350, "description": "10 публикаций"},
        "20": {"price": 600, "description": "20 публикаций"}
    }
    
    # Ссылки на оплату через ЮMoney (будут генерироваться динамически)
    YOOMONEY_BASE_URL = "https://yoomoney.ru/quickpay/confirm.xml"
    
    # Username канала
    CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "-1002369805353")  # ID канала "Барахолка - СПБ"
    
    # Username канала для ссылок (если есть)
    CHANNEL_USERNAME_LINK = os.getenv("CHANNEL_USERNAME_LINK", "baraxolkavspb")  # Username канала для ссылок
    
    # Красивое название канала для отображения
    CHANNEL_DISPLAY_NAME = os.getenv("CHANNEL_DISPLAY_NAME", "Барахолка СПБ")
    
    # ID администраторов
    admin_ids_str = os.getenv("ADMIN_USER_IDS", "476589798")
    print(f"DEBUG: admin_ids_str = '{admin_ids_str}'")
    ADMIN_USER_IDS = {int(x.strip()) for x in admin_ids_str.split(",") if x.strip()}
    print(f"DEBUG: ADMIN_USER_IDS = {ADMIN_USER_IDS}")
    
    # Путь к базе данных
    DATABASE_PATH = os.getenv("DATABASE_PATH", "auction_bot.db")
    
    # Внешние API настройки
    EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "")
    EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY", "")
    EXTERNAL_API_TIMEOUT = int(os.getenv("EXTERNAL_API_TIMEOUT", "30"))
    
    # IP-адреса для доступа к API (IPv4 и IPv6 через запятую)
    API_ALLOWED_IPS = os.getenv("API_ALLOWED_IPS", "")
    if API_ALLOWED_IPS:
        # Разделяем IP-адреса по запятым и очищаем от пробелов
        API_ALLOWED_IPS = [ip.strip() for ip in API_ALLOWED_IPS.split(",") if ip.strip()]
    else:
        API_ALLOWED_IPS = []
    
    # Настройки логирования
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "bot.log")
    
    # Настройки персистентности
    PERSISTENCE_FILE = os.getenv("PERSISTENCE_FILE", "auction_state.json")
    PERSISTENCE_INTERVAL = int(os.getenv("PERSISTENCE_INTERVAL", "300"))
    
    # Отключение проверки подписки (для тестирования)
    DISABLE_SUBSCRIPTION_CHECK = os.getenv("DISABLE_SUBSCRIPTION_CHECK", "true").lower() == "true"
    
    return {
        "BOT_TOKEN": BOT_TOKEN,
        "PAYMENTS_PROVIDER_TOKEN": PAYMENTS_PROVIDER_TOKEN,
        "YOOMONEY_RECEIVER": YOOMONEY_RECEIVER,
        "YOOMONEY_SECRET": YOOMONEY_SECRET,
        "YOOMONEY_NOTIFICATION_URL": YOOMONEY_NOTIFICATION_URL,
        "PAYMENT_PLANS": PAYMENT_PLANS,
        "YOOMONEY_BASE_URL": YOOMONEY_BASE_URL,
        "CHANNEL_USERNAME": CHANNEL_USERNAME,
        "CHANNEL_USERNAME_LINK": CHANNEL_USERNAME_LINK,
        "CHANNEL_DISPLAY_NAME": CHANNEL_DISPLAY_NAME,
        "ADMIN_USER_IDS": ADMIN_USER_IDS,
        "DATABASE_PATH": DATABASE_PATH,
        "EXTERNAL_API_URL": EXTERNAL_API_URL,
        "EXTERNAL_API_KEY": EXTERNAL_API_KEY,
        "EXTERNAL_API_TIMEOUT": EXTERNAL_API_TIMEOUT,
        "API_ALLOWED_IPS": API_ALLOWED_IPS,
        "LOG_LEVEL": LOG_LEVEL,
        "LOG_FILE": LOG_FILE,
        "PERSISTENCE_FILE": PERSISTENCE_FILE,
        "PERSISTENCE_INTERVAL": PERSISTENCE_INTERVAL,
        "DISABLE_SUBSCRIPTION_CHECK": DISABLE_SUBSCRIPTION_CHECK
    }

# Загружаем конфигурацию
config = load_config()

# Экспортируем константы
BOT_TOKEN = config["BOT_TOKEN"]
PAYMENTS_PROVIDER_TOKEN = config["PAYMENTS_PROVIDER_TOKEN"]
YOOMONEY_RECEIVER = config["YOOMONEY_RECEIVER"]
YOOMONEY_SECRET = config["YOOMONEY_SECRET"]
YOOMONEY_NOTIFICATION_URL = config["YOOMONEY_NOTIFICATION_URL"]
PAYMENT_PLANS = config["PAYMENT_PLANS"]
YOOMONEY_BASE_URL = config["YOOMONEY_BASE_URL"]
CHANNEL_USERNAME = config["CHANNEL_USERNAME"]
CHANNEL_USERNAME_LINK = config["CHANNEL_USERNAME_LINK"]
CHANNEL_DISPLAY_NAME = config["CHANNEL_DISPLAY_NAME"]
ADMIN_USER_IDS = config["ADMIN_USER_IDS"]
DATABASE_PATH = config["DATABASE_PATH"]
EXTERNAL_API_URL = config["EXTERNAL_API_URL"]
EXTERNAL_API_KEY = config["EXTERNAL_API_KEY"]
EXTERNAL_API_TIMEOUT = config["EXTERNAL_API_TIMEOUT"]
API_ALLOWED_IPS = config["API_ALLOWED_IPS"]
LOG_LEVEL = config["LOG_LEVEL"]
LOG_FILE = config["LOG_FILE"]
PERSISTENCE_FILE = config["PERSISTENCE_FILE"]
PERSISTENCE_INTERVAL = config["PERSISTENCE_INTERVAL"]
DISABLE_SUBSCRIPTION_CHECK = config["DISABLE_SUBSCRIPTION_CHECK"]
