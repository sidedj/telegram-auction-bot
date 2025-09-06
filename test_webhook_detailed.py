#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальный тест webhook с проверкой обработки данных
"""

import requests
import json
import time

def test_webhook_detailed():
    """Детальный тест webhook"""
    print("🚀 Детальный тест webhook")
    print("=" * 50)
    
    # URL нового endpoint
    url = "https://web-production-fa7dc.up.railway.app/webhook"
    
    # Тестовые данные в формате YooMoney
    test_data = {
        'notification_type': 'card-incoming',
        'operation_id': 'test_detailed_123',
        'amount': '50.00',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': '2025-09-06T17:00:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true',
        'sha1_hash': 'test_hash_123'
    }
    
    print("🧪 Тестируем webhook с полными данными...")
    print("📤 Отправляем данные:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(url, data=test_data, timeout=10)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook работает!")
            
            # Ждем немного, чтобы данные обработались
            print("\n⏳ Ждем обработки данных...")
            time.sleep(2)
            
            # Проверяем баланс
            print("\n🔍 Проверяем баланс...")
            check_balance_after_webhook()
            
            return True
        else:
            print("❌ Webhook не работает!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_balance_after_webhook():
    """Проверяем баланс после webhook"""
    import sqlite3
    import os
    
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
                print(f"💰 Текущий баланс: {balance} публикаций")
            else:
                print("❌ Пользователь не найден")
            
            # Проверяем последние транзакции
            cursor.execute("""
                SELECT amount, transaction_type, description, created_at 
                FROM transactions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 3
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
        print(f"❌ Ошибка проверки баланса: {e}")

if __name__ == "__main__":
    test_webhook_detailed()
