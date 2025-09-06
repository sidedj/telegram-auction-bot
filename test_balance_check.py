#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка баланса после webhook
"""

import sqlite3
import os

def check_balance():
    """Проверяем баланс пользователя"""
    print("🔍 Проверка баланса")
    print("=" * 30)
    
    # Путь к базе данных
    db_path = "auction_bot.db"
    
    if not os.path.exists(db_path):
        print("❌ База данных не найдена!")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Проверяем баланс пользователя 476589798
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (476589798,))
            result = cursor.fetchone()
            
            if result:
                balance = result[0]
                print(f"💰 Баланс пользователя 476589798: {balance} публикаций")
            else:
                print("❌ Пользователь не найден в базе данных")
            
            # Проверяем транзакции
            cursor.execute("""
                SELECT amount, transaction_type, description, created_at 
                FROM transactions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 5
            """, (476589798,))
            
            transactions = cursor.fetchall()
            
            if transactions:
                print(f"\n📋 Последние транзакции:")
                for trans in transactions:
                    amount, trans_type, desc, created_at = trans
                    print(f"   {created_at}: {amount} ({trans_type}) - {desc}")
            else:
                print("❌ Транзакции не найдены")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_balance()
