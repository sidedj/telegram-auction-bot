#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест баланса конкретного пользователя
"""

import requests
import json
import time
import hashlib

def test_user_balance():
    """Тестируем баланс пользователя 476589798"""
    print("🧪 Тест баланса пользователя 476589798")
    print("=" * 60)
    
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    user_id = 476589798
    
    # Тестовое пополнение на 50₽ = 1 публикация
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': f'balance_test_{int(time.time())}',
        'amount': '50.00',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': '2024-01-01T12:00:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': f'user_{user_id}',
        'test_notification': 'true'
    }
    
    # Вычисляем подпись
    sorted_keys = sorted(test_data.keys())
    string_to_sign = "&".join([f"{key}={test_data[key]}" for key in sorted_keys])
    signature = hashlib.sha1((string_to_sign + "SaTKEuJWPVXJI/JFpXDCHZ4q").encode('utf-8')).hexdigest()
    test_data['sha1_hash'] = signature
    
    print(f"📤 Отправляем пополнение на 50₽ для пользователя {user_id}")
    print(f"🎯 Ожидается: +1 публикация")
    
    try:
        response = requests.post(url, data=test_data, timeout=30)
        
        print(f"📥 Статус: {response.status_code}")
        print(f"📥 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook: OK")
            print("\n💡 Теперь проверьте в боте:")
            print("   1. Нажмите '📊 Статистика'")
            print("   2. Баланс должен показать 1 публикацию (или ∞ для админа)")
            print("   3. Нажмите 'Пополнить баланс'")
            print("   4. Там тоже должен быть правильный баланс")
        else:
            print("❌ Webhook: Ошибка")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_admin_balance():
    """Тестируем баланс администратора"""
    print("\n🔍 Тест баланса администратора")
    print("=" * 60)
    
    print("👑 Пользователь 476589798 является администратором")
    print("💡 Для админов должен показываться '∞ (администратор)'")
    print("💡 Если показывается 0, то есть проблема с логикой админов")

if __name__ == "__main__":
    print("🚀 Тест баланса пользователя")
    print("=" * 80)
    
    test_user_balance()
    test_admin_balance()
    
    print("\n" + "=" * 80)
    print("🎉 Тест завершен!")
    print("\n💡 Если баланс все еще показывает 0:")
    print("   1. Проверьте, что пользователь не является админом")
    print("   2. Проверьте, что webhook правильно обрабатывает платежи")
    print("   3. Проверьте, что баланс сохраняется в базе данных")
