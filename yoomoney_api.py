#!/usr/bin/env python3
"""
Модуль для работы с API ЮMoney
"""
import requests
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

class YooMoneyAPI:
    def __init__(self, receiver: str, secret: str):
        self.receiver = receiver
        self.secret = secret
        self.base_url = "https://yoomoney.ru/api"
        
    def get_operation_history(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        Получает историю операций из ЮMoney
        """
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=1)
            if not end_date:
                end_date = datetime.now()
            
            # Формируем параметры запроса
            params = {
                'type': 'deposition',
                'from': start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'till': end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'records': 100
            }
            
            # Создаем подпись запроса
            string_to_sign = f"GET&{self.base_url}/operation-history&{self._params_to_string(params)}"
            signature = hmac.new(
                self.secret.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha1
            ).hexdigest()
            
            headers = {
                'Authorization': f'Bearer {self.secret}',
                'X-Signature': signature
            }
            
            response = requests.get(
                f"{self.base_url}/operation-history",
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('operations', [])
            else:
                logging.error(f"Ошибка API ЮMoney: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"Ошибка при получении истории операций: {e}")
            return []
    
    def _params_to_string(self, params: Dict) -> str:
        """Преобразует параметры в строку для подписи"""
        return '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    
    def verify_webhook_signature(self, data: Dict, signature: str) -> bool:
        """
        Проверяет подпись webhook'а от ЮMoney
        """
        try:
            # Создаем строку для подписи
            string_to_sign = f"{data['notification_type']}&{data['operation_id']}&{data['amount']}&{data['currency']}&{data['datetime']}&{data['sender']}&{data['codepro']}&{self.secret}&{data.get('label', '')}"
            
            # Вычисляем SHA-1 хеш
            calculated_signature = hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()
            
            # Сравниваем с полученной подписью
            return hmac.compare_digest(calculated_signature, signature)
        except Exception as e:
            logging.error(f"Ошибка при проверке подписи: {e}")
            return False

class PaymentProcessor:
    def __init__(self, yoomoney_api: YooMoneyAPI, database_path: str):
        self.yoomoney_api = yoomoney_api
        self.database_path = database_path
        
    async def process_payment_from_webhook(self, data: Dict) -> bool:
        """
        Обрабатывает платеж из webhook'а
        """
        try:
            operation_id = data.get('operation_id')
            
            # Используем withdraw_amount (сумма без комиссии) для определения тарифа
            if 'withdraw_amount' in data and data['withdraw_amount']:
                amount = float(data['withdraw_amount'])
            else:
                amount = float(data.get('amount', 0))
            
            # Определяем количество публикаций по тарифу (сумма до комиссии)
            if amount == 50:
                publications = 1
            elif amount == 200:
                publications = 5
            elif amount == 350:
                publications = 10
            elif amount == 600:
                publications = 20
            else:
                # Если сумма не соответствует тарифам, зачисляем по 1₽ = 1 публикация
                publications = int(amount)
            
            # Получаем user_id из label
            user_id = None
            if 'label' in data and data['label']:
                label = data['label']
                if label.startswith('user_'):
                    try:
                        user_id = int(label.replace('user_', ''))
                    except ValueError:
                        logging.error(f"Неверный формат user_id в label: {label}")
                        return False
            
            # Если user_id не указан, используем sender как fallback
            if not user_id and sender:
                try:
                    user_id = int(sender)
                except ValueError:
                    logging.error(f"Неверный формат user_id в sender: {sender}")
                    return False
            
            if not user_id:
                logging.error("Не удалось определить user_id для платежа")
                return False
            
            # Проверяем, не обработан ли уже этот платеж
            import aiosqlite
            async with aiosqlite.connect(self.database_path) as db_conn:
                cursor = await db_conn.execute(
                    "SELECT operation_id FROM processed_payments WHERE operation_id = ?",
                    (operation_id,)
                )
                if await cursor.fetchone():
                    logging.warning(f"Платеж {operation_id} уже был обработан")
                    return True
                
                # Записываем платеж как обработанный
                await db_conn.execute(
                    "INSERT INTO processed_payments (operation_id, user_id, amount, publications) VALUES (?, ?, ?, ?)",
                    (operation_id, user_id, amount, publications)
                )
                
                # Создаем пользователя, если его нет
                await db_conn.execute(
                    "INSERT OR IGNORE INTO users (user_id, username, full_name, balance, is_admin) VALUES (?, ?, ?, ?, ?)",
                    (user_id, None, None, 0, False)
                )
                
                # Зачисляем средства на баланс
                await db_conn.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                    (publications, user_id)
                )
                
                # Записываем транзакцию
                await db_conn.execute(
                    "INSERT INTO transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)",
                    (user_id, publications, "yoomoney_payment", f"Пополнение через YooMoney: {amount} руб. (операция {operation_id})")
                )
                
                await db_conn.commit()
                
            logging.info(f"✅ Платеж обработан: пользователь {user_id}, сумма {amount} руб., публикаций {publications}")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка при обработке платежа: {e}")
            return False
    
    async def process_pending_payments(self) -> int:
        """
        Обрабатывает ожидающие платежи (для случаев, когда webhook не работает)
        """
        try:
            # Получаем последние операции из ЮMoney
            operations = self.yoomoney_api.get_operation_history()
            
            processed_count = 0
            
            for operation in operations:
                # Проверяем, что это входящий платеж
                if operation.get('type') != 'deposition':
                    continue
                
                operation_id = operation.get('operation_id')
                amount = float(operation.get('amount', 0))
                label = operation.get('label', '')
                
                # Получаем user_id из label
                user_id = None
                if label.startswith('user_'):
                    try:
                        user_id = int(label.replace('user_', ''))
                    except ValueError:
                        continue
                
                if not user_id:
                    continue
                
                # Проверяем, не обработан ли уже этот платеж
                import aiosqlite
                async with aiosqlite.connect(self.database_path) as db_conn:
                    cursor = await db_conn.execute(
                        "SELECT operation_id FROM processed_payments WHERE operation_id = ?",
                        (operation_id,)
                    )
                    if await cursor.fetchone():
                        continue
                    
                    # Обрабатываем платеж
                    publications = int(amount)
                    
                    # Записываем платеж как обработанный
                    await db_conn.execute(
                        "INSERT INTO processed_payments (operation_id, user_id, amount, publications) VALUES (?, ?, ?, ?)",
                        (operation_id, user_id, amount, publications)
                    )
                    
                    # Создаем пользователя, если его нет
                    await db_conn.execute(
                        "INSERT OR IGNORE INTO users (user_id, username, full_name, balance, is_admin) VALUES (?, ?, ?, ?, ?)",
                        (user_id, None, None, 0, False)
                    )
                    
                    # Зачисляем средства на баланс
                    await db_conn.execute(
                        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                        (publications, user_id)
                    )
                    
                    # Записываем транзакцию
                    await db_conn.execute(
                        "INSERT INTO transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)",
                        (user_id, publications, "yoomoney_payment", f"Пополнение через YooMoney: {amount} руб. (операция {operation_id})")
                    )
                    
                    await db_conn.commit()
                    processed_count += 1
                    
                    logging.info(f"✅ Обработан ожидающий платеж: пользователь {user_id}, сумма {amount} руб., публикаций {publications}")
            
            return processed_count
            
        except Exception as e:
            logging.error(f"Ошибка при обработке ожидающих платежей: {e}")
            return 0
