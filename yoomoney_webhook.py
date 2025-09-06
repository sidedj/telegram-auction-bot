#!/usr/bin/env python3
from flask import Flask, request
import hashlib
import hmac
import asyncio
import aiosqlite
import logging
from datetime import datetime
import os

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Секрет для проверки подлинности YooMoney
YOOMONEY_SECRET = "SaTKEuJWPVXJl/JFpXDCHZ4q"

# Путь к базе данных
DATABASE_PATH = "auction_bot.db"

def verify_yoomoney_signature(data, secret, signature):
    """
    Проверяет подлинность уведомления от YooMoney
    """
    try:
        # Создаем строку для подписи
        string_to_sign = f"{data['notification_type']}&{data['operation_id']}&{data['amount']}&{data['currency']}&{data['datetime']}&{data['sender']}&{data['codepro']}&{secret}&{data['label']}"
        
        # Вычисляем SHA-1 хеш
        calculated_signature = hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()
        
        # Сравниваем с полученной подписью
        return hmac.compare_digest(calculated_signature, signature)
    except Exception as e:
        logger.error(f"Ошибка при проверке подписи: {e}")
        return False

async def process_payment(data):
    """
    Обрабатывает платеж и зачисляет средства в бот
    """
    try:
        operation_id = data.get('operation_id')
        amount = float(data.get('amount', 0))
        sender = data.get('sender', '')
        
        # Конвертируем рубли в публикации (1 рубль = 1 публикация)
        publications = int(amount)
        
        # Получаем user_id из label (если указан)
        user_id = None
        if 'label' in data and data['label']:
            label = data['label']
            # Обрабатываем разные форматы label
            if label.startswith('user_'):
                # Формат: user_123456789
                try:
                    user_id = int(label.replace('user_', ''))
                except ValueError:
                    logger.error(f"Неверный формат user_id в label: {label}")
                    return False
            else:
                # Просто числовой ID
                try:
                    user_id = int(label)
                except ValueError:
                    logger.error(f"Неверный формат user_id в label: {label}")
                    return False
        
        # Если user_id не указан, используем sender как fallback
        if not user_id and sender:
            try:
                user_id = int(sender)
            except ValueError:
                logger.error(f"Неверный формат user_id в sender: {sender}")
                return False
        
        if not user_id:
            logger.error("Не удалось определить user_id для платежа")
            return False
        
        # Проверяем, не обработан ли уже этот платеж
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                "SELECT operation_id FROM processed_payments WHERE operation_id = ?",
                (operation_id,)
            )
            if await cursor.fetchone():
                logger.warning(f"Платеж {operation_id} уже был обработан")
                return True
            
            # Записываем платеж как обработанный
            await db.execute(
                "INSERT INTO processed_payments (operation_id, user_id, amount, publications) VALUES (?, ?, ?, ?)",
                (operation_id, user_id, amount, publications)
            )
            
            # Создаем пользователя, если его нет
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username, full_name, balance, is_admin) VALUES (?, ?, ?, ?, ?)",
                (user_id, None, None, 0, False)
            )
            
            # Зачисляем средства на баланс
            await db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (publications, user_id)
            )
            
            # Записываем транзакцию
            await db.execute(
                "INSERT INTO transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)",
                (user_id, publications, "yoomoney_payment", f"Пополнение через YooMoney: {amount} руб. (операция {operation_id})")
            )
            
            await db.commit()
            
        logger.info(f"✅ Платеж обработан: пользователь {user_id}, сумма {amount} руб., публикаций {publications}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при обработке платежа: {e}")
        return False

@app.route('/yoomoney', methods=['POST', 'GET'])
def yoomoney_webhook():
    """Webhook для обработки уведомлений от YooMoney"""
    try:
        logger.info("=" * 50)
        logger.info("ПОЛУЧЕН ЗАПРОС ОТ YOOMONEY")
        logger.info(f"Метод: {request.method}")
        logger.info(f"IP: {request.remote_addr}")
        
        if request.method == 'GET':
            return "OK"
        
        # Получаем данные
        data = request.form.to_dict()
        logger.info(f"Данные: {data}")
        
        # Проверяем обязательные поля
        required_fields = ['notification_type', 'operation_id', 'amount', 'currency', 'datetime', 'sender', 'codepro', 'sha1_hash']
        for field in required_fields:
            if field not in data:
                logger.error(f"Отсутствует обязательное поле: {field}")
                return "error", 400
        
        # Проверяем подлинность уведомления
        if not verify_yoomoney_signature(data, YOOMONEY_SECRET, data['sha1_hash']):
            logger.error("❌ Неверная подпись уведомления!")
            return "error", 400
        
        logger.info("✅ Подпись уведомления проверена")
        
        # Обрабатываем только входящие платежи
        if data['notification_type'] != 'p2p-incoming':
            logger.info(f"Пропускаем уведомление типа: {data['notification_type']}")
            return "OK"
        
        # Проверяем, что это не тестовое уведомление
        if data.get('test_notification') == 'true':
            logger.info("✅ Тестовое уведомление получено и проверено")
            return "OK"
        
        # Обрабатываем реальный платеж
        success = asyncio.run(process_payment(data))
        
        if success:
            logger.info("✅ Платеж успешно обработан")
            return "OK"
        else:
            logger.error("❌ Ошибка при обработке платежа")
            return "error", 500
            
    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "error", 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return {"status": "ok", "message": "YooMoney webhook is running"}

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
