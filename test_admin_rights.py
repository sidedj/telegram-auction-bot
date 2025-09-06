#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест админских прав
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import ADMIN_USER_IDS, BOT_TOKEN
from database import Database

async def test_admin_rights():
    """Тестируем админские права"""
    print("🔍 Проверка админских прав")
    print("=" * 40)
    
    # ID пользователя для проверки
    test_user_id = 476589798
    
    print(f"👤 Тестируем пользователя: {test_user_id}")
    print(f"🔑 BOT_TOKEN: {BOT_TOKEN[:10]}...")
    print(f"👑 ADMIN_USER_IDS: {ADMIN_USER_IDS}")
    
    # Проверяем, есть ли пользователь в списке админов
    is_in_config = test_user_id in ADMIN_USER_IDS
    print(f"⚙️ В конфигурации: {'✅ Да' if is_in_config else '❌ Нет'}")
    
    # Проверяем в базе данных
    try:
        db = Database()
        user = await db.get_or_create_user(test_user_id)
        
        print(f"💾 В базе данных:")
        print(f"   - is_admin: {'✅ Да' if user['is_admin'] else '❌ Нет'}")
        print(f"   - balance: {user['balance']}")
        print(f"   - username: {user.get('username', 'не указан')}")
        print(f"   - full_name: {user.get('full_name', 'не указано')}")
        
        # Проверяем, нужно ли обновить админские права
        if is_in_config and not user['is_admin']:
            print("🔄 Обновляем админские права...")
            await db.grant_admin_status(test_user_id)
            print("✅ Админские права обновлены!")
            
            # Проверяем еще раз
            user = await db.get_or_create_user(test_user_id)
            print(f"💾 После обновления - is_admin: {'✅ Да' if user['is_admin'] else '❌ Нет'}")
        
    except Exception as e:
        print(f"❌ Ошибка работы с базой данных: {e}")
    
    print("\n📋 Список всех админов в конфигурации:")
    for admin_id in ADMIN_USER_IDS:
        print(f"   - {admin_id}")

if __name__ == "__main__":
    asyncio.run(test_admin_rights())
