#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест нового webhook endpoint
"""

import requests
import json

def test_new_webhook():
    """Тестируем новый webhook endpoint"""
    print("🚀 Тест нового webhook")
    print("=" * 50)
    
    # URL нового endpoint
    url = "https://web-production-fa7dc.up.railway.app/webhook"
    
    # Тестовые данные
    test_data = {
        'notification_type': 'card-incoming',
        'test_notification': 'true',
        'amount': '10.00',
        'currency': '643',
        'label': 'test_label'
    }
    
    print("🧪 Тестируем новый webhook...")
    print("📤 Отправляем данные:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(url, data=test_data, timeout=10)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        print(f"   Заголовки: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Webhook работает!")
            return True
        else:
            print("❌ Webhook не работает!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_new_webhook()
