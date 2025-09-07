# Файл: timezone_utils.py
# Утилиты для работы с московским временем

import pytz
from datetime import datetime, timedelta
from typing import Optional

# Московский часовой пояс
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

def get_moscow_time() -> datetime:
    """Получить текущее время в московском часовом поясе"""
    return datetime.now(MOSCOW_TZ)

def get_moscow_time_naive() -> datetime:
    """Получить текущее время в московском часовом поясе без информации о часовом поясе"""
    return get_moscow_time().replace(tzinfo=None)

def format_moscow_time(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
    """Форматировать время в московском часовом поясе"""
    if dt.tzinfo is None:
        # Если время без часового пояса, считаем его московским
        dt = MOSCOW_TZ.localize(dt)
    elif dt.tzinfo != MOSCOW_TZ:
        # Если время в другом часовом поясе, конвертируем в московское
        dt = dt.astimezone(MOSCOW_TZ)
    
    return dt.strftime(format_str)

def parse_moscow_time(time_str: str, format_str: str = "%d.%m.%Y %H:%M") -> datetime:
    """Парсить строку времени как московское время"""
    dt = datetime.strptime(time_str, format_str)
    return MOSCOW_TZ.localize(dt)

def get_time_until_moscow(target_time: datetime) -> timedelta:
    """Получить время до указанного момента в московском времени"""
    now = get_moscow_time()
    if target_time.tzinfo is None:
        target_time = MOSCOW_TZ.localize(target_time)
    elif target_time.tzinfo != MOSCOW_TZ:
        target_time = target_time.astimezone(MOSCOW_TZ)
    
    return target_time - now

def format_time_left(delta: timedelta) -> str:
    """Форматировать оставшееся время в читаемый вид"""
    if delta.total_seconds() <= 0:
        return "⏰ Время истекло"
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"⏰ {days}д {hours}ч {minutes}м"
    elif hours > 0:
        return f"⏰ {hours}ч {minutes}м"
    elif minutes > 0:
        return f"⏰ {minutes}м {seconds}с"
    else:
        return f"⏰ {seconds}с"

# Для обратной совместимости
def now() -> datetime:
    """Получить текущее московское время (без информации о часовом поясе)"""
    return get_moscow_time_naive()
