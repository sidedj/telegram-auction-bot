#!/usr/bin/env python3
"""
Стартовый файл для Railway
Запускает Flask сервер для webhook
"""

import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Запуск webhook сервера через start_payment_server.py")
    
    # Импортируем и запускаем Flask приложение из bot.py
    from bot import app
    import logging
    
    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO)
    
    # Получаем порт из переменной окружения Railway
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🌐 Запуск сервера на порту {port}")
    
    # Запускаем Flask приложение
    app.run(host="0.0.0.0", port=port, debug=False)
