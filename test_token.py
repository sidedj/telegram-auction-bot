#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест токена бота
"""

import asyncio
from aiogram import Bot
from config import BOT_TOKEN

async def test_token():
    """Тестируем токен бота"""
    print("🔑 Тест токена бота")
    print("=" * 30)
    
    print(f"Токен: {BOT_TOKEN}")
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"✅ Бот работает!")
        print(f"   ID: {bot_info.id}")
        print(f"   Username: @{bot_info.username}")
        print(f"   First Name: {bot_info.first_name}")
        
        # Закрываем бота
        await bot.session.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("💡 Возможные причины:")
        print("   - Неправильный токен")
        print("   - Бот не создан в @BotFather")
        print("   - Проблемы с интернетом")

if __name__ == "__main__":
    asyncio.run(test_token())
