#!/usr/bin/env python3
"""
Тест системы уведомлений
"""
import asyncio
import logging
from notifications import NotificationManager

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Токен бота (замените на ваш)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def test_notifications():
    """Тестирует все типы уведомлений"""
    
    # Инициализируем менеджер уведомлений
    notification_manager = NotificationManager(BOT_TOKEN)
    
    # Тестовый user_id (замените на реальный)
    test_user_id = 123456789
    
    print("🧪 Тестирование системы уведомлений...")
    
    try:
        # Тест 1: Уведомление о пополнении баланса
        print("\n1️⃣ Тестируем уведомление о пополнении баланса...")
        success = await notification_manager.send_balance_notification(
            user_id=test_user_id,
            amount=50.0,
            publications=1,
            new_balance=5
        )
        print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
        
        # Тест 2: Уведомление о создании аукциона
        print("\n2️⃣ Тестируем уведомление о создании аукциона...")
        success = await notification_manager.send_auction_created_notification(
            user_id=test_user_id,
            auction_description="Тестовый товар для продажи",
            auction_id=12345
        )
        print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
        
        # Тест 3: Уведомление о публикации аукциона
        print("\n3️⃣ Тестируем уведомление о публикации аукциона...")
        success = await notification_manager.send_auction_published_notification(
            user_id=test_user_id,
            auction_description="Тестовый товар для продажи",
            remaining_balance=4,
            is_admin=False
        )
        print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
        
        # Тест 4: Уведомление о завершении аукциона (для продавца)
        print("\n4️⃣ Тестируем уведомление о завершении аукциона (продавец)...")
        success = await notification_manager.send_auction_ended_notification(
            user_id=test_user_id,
            auction_description="Тестовый товар для продажи",
            final_price=150.0,
            winner_id=987654321
        )
        print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
        
        # Тест 5: Уведомление о завершении аукциона (для покупателя)
        print("\n5️⃣ Тестируем уведомление о завершении аукциона (покупатель)...")
        success = await notification_manager.send_auction_ended_notification(
            user_id=987654321,
            auction_description="Тестовый товар для продажи",
            final_price=150.0,
            winner_id=987654321
        )
        print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
        
        print("\n🎉 Тестирование завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    
    finally:
        # Закрываем соединение
        await notification_manager.close()

async def test_webhook_notification():
    """Тестирует уведомление через webhook"""
    print("\n🔗 Тестируем webhook уведомление...")
    
    # Импортируем функцию из bot.py
    try:
        from notifications import send_balance_notification
        
        # Тестовые данные
        test_user_id = 123456789
        amount = 50.0
        publications = 1
        new_balance = 5
        
        success = await send_balance_notification(
            user_id=test_user_id,
            amount=amount,
            publications=publications,
            new_balance=new_balance
        )
        
        print(f"   Webhook уведомление: {'✅ Успешно' if success else '❌ Ошибка'}")
        
    except Exception as e:
        print(f"❌ Ошибка webhook теста: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов системы уведомлений")
    print("⚠️  Внимание: Убедитесь, что BOT_TOKEN указан правильно!")
    
    # Запускаем тесты
    asyncio.run(test_notifications())
    asyncio.run(test_webhook_notification())
    
    print("\n✨ Все тесты завершены!")
