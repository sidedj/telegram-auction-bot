# Файл: payment_server.py

import asyncio
import logging
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any
from flask import Flask, request, jsonify
import threading
import queue

from config import YOOMONEY_SECRET, DATABASE_PATH, PAYMENT_PLANS
from yoomoney_payment import YooMoneyPayment
from database import Database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Очередь для уведомлений боту
notification_queue = queue.Queue()

class PaymentProcessor:
    """Класс для обработки платежей и защиты от накрутки"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.yoomoney = YooMoneyPayment()
        self.processed_operations = set()  # Для защиты от повторной обработки
        
    def is_operation_processed(self, operation_id: str) -> bool:
        """Проверяет, была ли операция уже обработана"""
        return operation_id in self.processed_operations
    
    def mark_operation_processed(self, operation_id: str):
        """Отмечает операцию как обработанную"""
        self.processed_operations.add(operation_id)
    
    def validate_payment_amount(self, amount: str, plan_id: str) -> bool:
        """Проверяет соответствие суммы тарифному плану"""
        try:
            payment_amount = float(amount)
            if plan_id in PAYMENT_PLANS:
                expected_amount = PAYMENT_PLANS[plan_id]["price"]
                return abs(payment_amount - expected_amount) < 0.01  # Учитываем погрешность
            return False
        except ValueError:
            return False
    
    def add_publications_to_user(self, user_id: int, plan_id: str) -> bool:
        """Добавляет публикации пользователю в базу данных"""
        try:
            if plan_id not in PAYMENT_PLANS:
                logger.error(f"Неизвестный план: {plan_id}")
                return False
            
            publications_count = int(plan_id)
            
            # Подключаемся к базе данных
            db = Database(self.db_path)
            
            # Получаем текущий баланс пользователя синхронно
            current_balance = self.get_user_balance_sync(user_id)
            if current_balance is None:
                # Если пользователя нет в базе, создаем его
                self.add_user_sync(user_id, 0)
                current_balance = 0
            
            # Добавляем публикации
            new_balance = current_balance + publications_count
            self.update_user_balance_sync(user_id, new_balance)
            
            logger.info(f"Пользователю {user_id} добавлено {publications_count} публикаций. Новый баланс: {new_balance}")
            
            # Добавляем запись в историю платежей
            self.log_payment(user_id, plan_id, publications_count)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении публикаций пользователю {user_id}: {e}")
            return False
    
    def get_user_balance_sync(self, user_id: int) -> Optional[int]:
        """Синхронное получение баланса пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Ошибка при получении баланса пользователя {user_id}: {e}")
            return None
    
    def add_user_sync(self, user_id: int, balance: int = 0):
        """Синхронное добавление пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        full_name TEXT,
                        balance INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_admin BOOLEAN DEFAULT FALSE
                    )
                """)
                
                cursor.execute("""
                    INSERT OR IGNORE INTO users (user_id, balance)
                    VALUES (?, ?)
                """, (user_id, balance))
                
                conn.commit()
                logger.info(f"Пользователь {user_id} добавлен с балансом {balance}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
    
    def update_user_balance_sync(self, user_id: int, new_balance: int):
        """Синхронное обновление баланса пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET balance = ? WHERE user_id = ?
                """, (new_balance, user_id))
                
                conn.commit()
                logger.info(f"Баланс пользователя {user_id} обновлен до {new_balance}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении баланса пользователя {user_id}: {e}")

    def log_payment(self, user_id: int, plan_id: str, publications_count: int):
        """Логирует информацию о платеже"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS payment_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        plan_id TEXT NOT NULL,
                        publications_count INTEGER NOT NULL,
                        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO payment_history (user_id, plan_id, publications_count)
                    VALUES (?, ?, ?)
                """, (user_id, plan_id, publications_count))
                
                conn.commit()
                logger.info(f"Платеж записан в историю: пользователь {user_id}, план {plan_id}")
                
        except Exception as e:
            logger.error(f"Ошибка при записи в историю платежей: {e}")

# Создаем экземпляр процессора платежей
payment_processor = PaymentProcessor(DATABASE_PATH)

@app.route("/yoomoney", methods=["POST"])
def yoomoney_notify():
    """Обработчик уведомлений от ЮMoney"""
    try:
        # Получаем данные от ЮMoney
        notification_data = request.form.to_dict()
        
        logger.info(f"Получено уведомление от ЮMoney: {notification_data}")
        logger.info(f"Payment processor yoomoney: {payment_processor.yoomoney}")
        
        # Проверяем секретное слово
        notification_secret = notification_data.get("notification_secret")
        if notification_secret != YOOMONEY_SECRET:
            logger.warning(f"Неверный секрет: {notification_secret}")
            return "error", 403
        
        # Валидируем данные уведомления
        try:
            is_valid, error_message = payment_processor.yoomoney.validate_payment_data(notification_data)
            logger.info(f"Валидация данных: valid={is_valid}, message={error_message}")
        except Exception as e:
            logger.error(f"Ошибка при валидации данных: {e}")
            return "error", 500
            
        if not is_valid:
            logger.warning(f"Невалидные данные уведомления: {error_message}")
            return "error", 400
        
        # Извлекаем данные
        operation_id = notification_data.get("operation_id")
        label = notification_data.get("label")
        amount = notification_data.get("amount")
        
        # Проверяем, не обрабатывалась ли уже эта операция
        if payment_processor.is_operation_processed(operation_id):
            logger.warning(f"Операция {operation_id} уже была обработана")
            return "OK", 200
        
        # Извлекаем ID пользователя
        user_id = payment_processor.yoomoney.extract_user_id_from_label(label)
        if user_id is None:
            logger.error(f"Не удалось извлечь ID пользователя из label: {label}")
            return "error", 400
        
        # Определяем план по сумме
        plan_id = None
        for pid, plan in PAYMENT_PLANS.items():
            if payment_processor.validate_payment_amount(amount, pid):
                plan_id = pid
                break
        
        if plan_id is None:
            logger.error(f"Неизвестная сумма платежа: {amount}")
            return "error", 400
        
        # Добавляем публикации пользователю
        success = payment_processor.add_publications_to_user(user_id, plan_id)
        if not success:
            logger.error(f"Не удалось добавить публикации пользователю {user_id}")
            return "error", 500
        
        # Отмечаем операцию как обработанную
        payment_processor.mark_operation_processed(operation_id)
        
        # Добавляем уведомление в очередь для бота
        notification_queue.put({
            "user_id": user_id,
            "plan_id": plan_id,
            "publications_count": int(plan_id),
            "amount": amount,
            "operation_id": operation_id
        })
        
        logger.info(f"Платеж успешно обработан: пользователь {user_id}, план {plan_id}, сумма {amount}")
        return "OK", 200
        
    except Exception as e:
        logger.error(f"Ошибка при обработке уведомления: {e}")
        return "error", 500

@app.route("/health", methods=["GET"])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route("/payment-history/<int:user_id>", methods=["GET"])
def get_payment_history(user_id: int):
    """Получение истории платежей пользователя"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT plan_id, publications_count, payment_date
                FROM payment_history
                WHERE user_id = ?
                ORDER BY payment_date DESC
                LIMIT 10
            """, (user_id,))
            
            history = cursor.fetchall()
            
            return jsonify({
                "user_id": user_id,
                "history": [
                    {
                        "plan_id": row[0],
                        "publications_count": row[1],
                        "payment_date": row[2]
                    }
                    for row in history
                ]
            })
            
    except Exception as e:
        logger.error(f"Ошибка при получении истории платежей: {e}")
        return jsonify({"error": "Internal server error"}), 500

def get_notification_queue():
    """Возвращает очередь уведомлений для бота"""
    return notification_queue

def start_payment_server(host="0.0.0.0", port=5000, debug=False):
    """Запускает сервер обработки платежей"""
    logger.info(f"Запуск сервера платежей на {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    start_payment_server(debug=True)
