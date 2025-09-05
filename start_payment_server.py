#!/usr/bin/env python3
"""
Временный файл для совместимости с Railway.
Запускает основной бот с webhook сервером.
"""

import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем основной бот
if __name__ == "__main__":
    # Устанавливаем переменную окружения для Railway
    os.environ["RAILWAY_ENVIRONMENT"] = "production"
    
    # Импортируем и запускаем бот
    from bot import run_bot_with_webhook
    run_bot_with_webhook()
