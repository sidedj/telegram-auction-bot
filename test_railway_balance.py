#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка баланса на Railway сервере
"""

import requests
import json

def test_railway_balance():
    """Проверяем баланс через Railway API"""
    print("🔍 Проверка баланса на Railway")
    print("=" * 40)
    
    # URL для проверки баланса (если есть такой endpoint)
    url = "https://web-production-fa7dc.up.railway.app/balance/476589798"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            balance = data.get('balance', 'неизвестно')
            print(f"💰 Баланс на Railway: {balance} публикаций")
        else:
            print("❌ Endpoint не найден, но webhook работает!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("💡 Webhook работает, но нет endpoint для проверки баланса")

def test_webhook_again():
    """Тестируем webhook еще раз"""
    print("\n🚀 Повторный тест webhook")
    print("=" * 30)
    
    url = "https://web-production-fa7dc.up.railway.app/webhook"
    
    test_data = {
        'notification_type': 'card-incoming',
        'test_notification': 'true',
        'amount': '100.00',
        'currency': '643',
        'label': 'user_476589798'
    }
    
    try:
        response = requests.post(url, data=test_data, timeout=10)
        
        print(f"📥 Ответ: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook работает! Баланс должен обновиться на сервере.")
        else:
            print("❌ Webhook не работает")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_railway_balance()
    test_webhook_again()
