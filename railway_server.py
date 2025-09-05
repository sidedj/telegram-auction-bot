#!/usr/bin/env python3
"""
Webhook сервер для Railway (только обработка платежей)
"""

import os
import sys
import logging
from flask import Flask, request, jsonify
import sqlite3
import requests
from datetime import datetime

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask приложение для webhook
app = Flask(__name__)

# Настройки
YOOMONEY_SECRET = "SaTKEuJWPVXJI/JFpXDCHZ4q"
DATABASE_PATH = "auction_bot.db"
BOT_TOKEN = "8486386170:AAEGHCYOtGlx3TrmZ3e9vQ7p8PbtCgs0YMw"

def init_database():
    """Инициализирует базу данных"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")

def get_user_balance(user_id: int) -> int:
    """Получает баланс пользователя"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Ошибка при получении баланса пользователя {user_id}: {e}")
        return 0

def update_user_balance(user_id: int, new_balance: int):
    """Обновляет баланс пользователя"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Проверяем, есть ли пользователь в базе
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                # Обновляем существующего пользователя
                cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            else:
                # Создаем нового пользователя
                cursor.execute("INSERT INTO users (user_id, balance, created_at) VALUES (?, ?, datetime('now'))", (user_id, new_balance))
            conn.commit()
            logger.info(f"Баланс пользователя {user_id} обновлен: {new_balance}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении баланса пользователя {user_id}: {e}")

def add_transaction(user_id: int, amount: int, transaction_type: str, description: str = None):
    """Добавляет транзакцию в базу данных"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)",
                (user_id, amount, transaction_type, description)
            )
            conn.commit()
            logger.info(f"Транзакция добавлена: пользователь {user_id}, сумма {amount}, тип {transaction_type}, описание {description}")
            
            # Проверяем, что транзакция действительно записалась
            cursor.execute(
                "SELECT COUNT(*) FROM transactions WHERE user_id = ? AND transaction_type = ?",
                (user_id, transaction_type)
            )
            count = cursor.fetchone()[0]
            logger.info(f"Всего транзакций типа '{transaction_type}' для пользователя {user_id}: {count}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении транзакции: {e}")

def send_telegram_message(user_id: int, message: str):
    """Отправляет сообщение пользователю в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': user_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"Сообщение отправлено пользователю {user_id}")
        else:
            logger.error(f"Ошибка отправки сообщения: {response.status_code}")
    except Exception as e:
        logger.error(f"Ошибка отправки Telegram сообщения: {e}")

@app.route('/health')
def health():
    """Проверка здоровья сервера"""
    return {"status": "ok", "message": "Railway server is running"}

@app.route('/yoomoney', methods=['POST'])
def yoomoney_webhook():
    """Обработка уведомлений от ЮMoney"""
    try:
        logger.info("Получено уведомление от ЮMoney")
        logger.info(f"Данные: {request.form.to_dict()}")
        
        # Получаем данные из формы
        notification_data = request.form.to_dict()
        
        # Проверяем, что это реальный платеж (не тестовый)
        if notification_data.get('test_notification') == 'true':
            logger.info("Получено тестовое уведомление, пропускаем")
            return "ok", 200
        
        # Для реальных платежей проверяем наличие обязательных полей
        if not notification_data.get('operation_id') or not notification_data.get('datetime'):
            logger.warning("Отсутствуют обязательные поля для реального платежа")
            return "error", 400
        
        # Проверяем, что операция подтверждена
        if notification_data.get('unaccepted') != 'false':
            logger.warning("Операция не подтверждена")
            return "error", 400
        
        # Получаем сумму и ID пользователя
        amount = float(notification_data.get('amount', 0))
        label = notification_data.get('label', '')
        
        if not label:
            logger.warning("Отсутствует label в уведомлении")
            return "error", 400
        
        # Извлекаем ID пользователя из label (формат: user_123456)
        if not label.startswith('user_'):
            logger.warning(f"Неверный формат label: {label}")
            return "error", 400
        
        try:
            user_id = int(label.replace('user_', ''))
        except ValueError:
            logger.warning(f"Неверный формат ID пользователя в label: {label}")
            return "error", 400
        
        # Определяем количество публикаций по сумме (учитывая комиссию ЮMoney)
        if amount >= 48.0 and amount <= 52.0:  # 50₽ с комиссией (48.50₽)
            publications = 1
        elif amount >= 195.0 and amount <= 205.0:  # 200₽ с комиссией (~198₽)
            publications = 5
        elif amount >= 340.0 and amount <= 360.0:  # 350₽ с комиссией (~348₽)
            publications = 10
        elif amount >= 590.0 and amount <= 610.0:  # 600₽ с комиссией (~598₽)
            publications = 20
        else:
            logger.warning(f"Неизвестная сумма: {amount} ₽ (с учетом комиссии ЮMoney)")
            return "error", 400
        
        # Получаем текущий баланс
        current_balance = get_user_balance(user_id)
        new_balance = current_balance + publications
        
        # Определяем номинальную сумму для отображения клиенту
        if amount >= 48.0 and amount <= 52.0:
            display_amount = 50
        elif amount >= 195.0 and amount <= 205.0:
            display_amount = 200
        elif amount >= 340.0 and amount <= 360.0:
            display_amount = 350
        elif amount >= 590.0 and amount <= 610.0:
            display_amount = 600
        else:
            display_amount = amount  # fallback
        
        # Обновляем баланс
        update_user_balance(user_id, new_balance)
        
        # Записываем транзакцию
        add_transaction(user_id, publications, 'purchase', f'Покупка {publications} публикаций за {display_amount}₽')
        
        # Отправляем уведомление пользователю (показываем номинальную сумму)
        message = f"💰 <b>Платеж получен!</b>\n\n"
        message += f"Сумма: {display_amount} ₽\n"
        message += f"Начислено: {publications} публикаций\n"
        message += f"Ваш баланс: {new_balance} публикаций"
        
        send_telegram_message(user_id, message)
        
        logger.info(f"Пользователю {user_id} начислено {publications} публикаций. Новый баланс: {new_balance}")
        
        return "ok", 200
        
    except Exception as e:
        logger.error(f"Ошибка при обработке уведомления: {e}")
        return "error", 500

def main():
    """Главная функция"""
    logger.info("🚀 Запуск Railway webhook сервера...")
    
    # Инициализируем базу данных
    init_database()
    
    # Запускаем Flask сервер
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"🌐 Webhook сервер запущен на порту {port}")
    logger.info(f"🔗 Webhook URL: /yoomoney")
    logger.info(f"🏥 Health check: /health")
    logger.info("⚠️ Бот запущен отдельно локально")
    
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":
    main()
