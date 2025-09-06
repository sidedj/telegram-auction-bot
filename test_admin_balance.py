#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест неограниченного баланса админа
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database

async def test_admin_balance():
    """Тестируем неограниченный баланс админа"""
    print("🔍 Тест неограниченного баланса админа")
    print("=" * 50)
    
    # ID админа
    admin_id = 476589798
    
    try:
        db = Database()
        
        # Получаем информацию о пользователе
        user = await db.get_or_create_user(admin_id)
        print(f"👤 Пользователь: {admin_id}")
        print(f"👑 is_admin: {'✅ Да' if user['is_admin'] else '❌ Нет'}")
        print(f"💰 balance в базе: {user['balance']}")
        
        # Тестируем функцию get_user_balance
        balance = await db.get_user_balance(admin_id)
        print(f"💰 get_user_balance: {balance}")
        
        if balance == 999999:
            print("✅ Неограниченный баланс работает!")
        else:
            print("❌ Неограниченный баланс не работает!")
            
        # Тестируем для обычного пользователя
        normal_user_id = 123456789
        normal_user = await db.get_or_create_user(normal_user_id)
        normal_balance = await db.get_user_balance(normal_user_id)
        
        print(f"\n👤 Обычный пользователь: {normal_user_id}")
        print(f"👑 is_admin: {'✅ Да' if normal_user['is_admin'] else '❌ Нет'}")
        print(f"💰 get_user_balance: {normal_balance}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_admin_balance())
