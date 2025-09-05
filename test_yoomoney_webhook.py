#!/usr/bin/env python3
"""
Тестирование webhook для ЮMoney
"""

import requests
import json

def test_yoomoney_webhook():
    """Тестирует webhook ЮMoney"""
    
    # URL вашего webhook сервера
    webhook_url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    # Тестовые данные (имитация уведомления от ЮMoney)
    test_data = {
        "notification_type": "p2p-incoming",
        "sha1_hash": "SaTKEuJWPVXJI/JFpXDCHZ4q",  # ЮMoney отправляет секрет в sha1_hash
        "label": "user_7647551803",  # Ваш ID пользователя
        "amount": "50.00",
        "operation_id": "test_operation_123",
        "unaccepted": "false",
        "datetime": "2024-01-01T12:00:00Z",
        "sender": "test_sender",
        "codepro": "false"
    }
    
    print("🧪 Тестирование webhook ЮMoney...")
    print(f"URL: {webhook_url}")
    print(f"Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(webhook_url, data=test_data, timeout=30)
        
        print(f"\n📊 Результат:")
        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook работает корректно!")
        else:
            print("❌ Ошибка в webhook")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

def test_health_endpoint():
    """Тестирует endpoint здоровья сервера"""
    
    health_url = "https://web-production-fa7dc.up.railway.app/health"
    
    print("\n🏥 Тестирование health endpoint...")
    print(f"URL: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Сервер работает!")
        else:
            print("❌ Проблема с сервером")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при подключении к серверу: {e}")

if __name__ == "__main__":
    print("=== ТЕСТИРОВАНИЕ WEBHOOK ЮMONEY ===\n")
    
    # Сначала проверим, что сервер работает
    test_health_endpoint()
    
    # Затем протестируем webhook
    test_yoomoney_webhook()
    
    print("\n=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")
