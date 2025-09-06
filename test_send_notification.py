#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест отправки уведомления
"""

import asyncio
from notifications import send_balance_notification

async def test_send_notification():
    """Тестируем отправку уведомления"""
    print("📱 Тест отправки уведомления")
    print("=" * 40)
    
    # ID админа для тестирования
    user_id = 476589798
    
    try:
        print(f"📤 Отправляем уведомление пользователю {user_id}...")
        
        await send_balance_notification(
            user_id=user_id,
            amount=200.0,  # Рубли
            publications=4,  # Публикации
            new_balance=999999  # Новый баланс
        )
        
        print("✅ Уведомление отправлено!")
        print("💡 Проверьте Telegram - должно прийти сообщение о пополнении баланса")
        
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")

if __name__ == "__main__":
    asyncio.run(test_send_notification())
