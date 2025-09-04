#!/usr/bin/env python3
# Файл: start_payment_server.py

"""
Скрипт для запуска сервера обработки платежей ЮMoney
"""

import logging
import sys
import os
from payment_server import start_payment_server

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('payment_server.log')
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Параметры сервера
        host = os.getenv("PAYMENT_SERVER_HOST", "0.0.0.0")
        port = int(os.getenv("PORT", os.getenv("PAYMENT_SERVER_PORT", "8080")))
        debug = os.getenv("PAYMENT_SERVER_DEBUG", "false").lower() == "true"
        
        logger.info(f"🚀 Запуск сервера платежей...")
        logger.info(f"📡 Адрес: http://{host}:{port}")
        logger.info(f"🔗 Webhook URL: http://{host}:{port}/yoomoney")
        logger.info(f"💊 Health check: http://{host}:{port}/health")
        
        # Запускаем сервер
        start_payment_server(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        logger.info("⛔ Сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)