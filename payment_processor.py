#!/usr/bin/env python3
"""
Автоматическая система обработки платежей
"""
import asyncio
import logging
from datetime import datetime, timedelta
from yoomoney_api import YooMoneyAPI, PaymentProcessor
from config import YOOMONEY_RECEIVER, YOOMONEY_SECRET, DATABASE_PATH

class AutomaticPaymentSystem:
    def __init__(self):
        self.yoomoney_api = YooMoneyAPI(YOOMONEY_RECEIVER, YOOMONEY_SECRET)
        self.payment_processor = PaymentProcessor(self.yoomoney_api, DATABASE_PATH)
        self.is_running = False
        
    async def start(self):
        """Запускает автоматическую систему обработки платежей"""
        self.is_running = True
        logging.info("🚀 Автоматическая система обработки платежей запущена")
        
        while self.is_running:
            try:
                # Обрабатываем ожидающие платежи каждые 5 минут
                processed_count = await self.payment_processor.process_pending_payments()
                
                if processed_count > 0:
                    logging.info(f"✅ Обработано {processed_count} ожидающих платежей")
                else:
                    logging.debug("Нет новых платежей для обработки")
                
                # Ждем 5 минут до следующей проверки
                await asyncio.sleep(300)  # 5 минут
                
            except Exception as e:
                logging.error(f"Ошибка в автоматической системе обработки платежей: {e}")
                await asyncio.sleep(60)  # Ждем минуту при ошибке
    
    async def stop(self):
        """Останавливает автоматическую систему"""
        self.is_running = False
        logging.info("🛑 Автоматическая система обработки платежей остановлена")
    
    async def process_single_payment(self, operation_id: str) -> bool:
        """Обрабатывает один платеж по ID операции"""
        try:
            # Получаем историю операций
            operations = self.yoomoney_api.get_operation_history()
            
            # Ищем нужную операцию
            for operation in operations:
                if operation.get('operation_id') == operation_id:
                    # Обрабатываем платеж
                    data = {
                        'operation_id': operation.get('operation_id'),
                        'amount': str(operation.get('amount', 0)),
                        'currency': '643',
                        'datetime': operation.get('datetime', ''),
                        'sender': operation.get('sender', ''),
                        'codepro': 'false',
                        'label': operation.get('label', '')
                    }
                    
                    return await self.payment_processor.process_payment_from_webhook(data)
            
            logging.warning(f"Платеж {operation_id} не найден в истории операций")
            return False
            
        except Exception as e:
            logging.error(f"Ошибка при обработке платежа {operation_id}: {e}")
            return False

# Глобальный экземпляр системы
payment_system = AutomaticPaymentSystem()

async def start_payment_processing():
    """Запускает обработку платежей в фоне"""
    await payment_system.start()

async def stop_payment_processing():
    """Останавливает обработку платежей"""
    await payment_system.stop()

async def process_payment_by_id(operation_id: str) -> bool:
    """Обрабатывает платеж по ID операции"""
    return await payment_system.process_single_payment(operation_id)
