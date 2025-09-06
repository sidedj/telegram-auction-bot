#!/usr/bin/env python3
"""
Тест автоматической системы обработки платежей
"""
import asyncio
import logging
from payment_processor import payment_system

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_automatic_system():
    """Тестирует автоматическую систему обработки платежей"""
    print("🧪 Тестирование автоматической системы обработки платежей...")
    
    try:
        # Запускаем систему
        print("🚀 Запускаем автоматическую систему...")
        await payment_system.start()
        
        # Ждем 30 секунд для обработки
        print("⏳ Ждем 30 секунд для обработки платежей...")
        await asyncio.sleep(30)
        
        # Останавливаем систему
        print("🛑 Останавливаем систему...")
        await payment_system.stop()
        
        print("✅ Тест завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

async def test_single_payment():
    """Тестирует обработку одного платежа"""
    print("🧪 Тестирование обработки одного платежа...")
    
    # Тестовый ID операции (замените на реальный)
    operation_id = "test_operation_123"
    
    try:
        success = await payment_system.process_single_payment(operation_id)
        
        if success:
            print("✅ Платеж успешно обработан!")
        else:
            print("❌ Ошибка при обработке платежа!")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов автоматической системы...")
    
    # Тестируем обработку одного платежа
    asyncio.run(test_single_payment())
    
    # Тестируем автоматическую систему (закомментировано для безопасности)
    # asyncio.run(test_automatic_system())
    
    print("✅ Все тесты завершены!")
