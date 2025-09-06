#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def test_webhook():
    """Тестирует webhook с детальным логированием"""
    
    url = "https://telegabot-production-3c68.up.railway.app/yoomoney"
    
    # Тестовые данные
    test_data = {
        'notification_type': 'p2p-incoming',
        'bill_id': '',
        'amount': '100.00',
        'datetime': '2025-09-06T07:20:00Z',
        'codepro': 'false',
        'sender': '41001000040',
        'sha1_hash': 'test_hash',
        'test_notification': 'true',
        'operation_label': '',
        'operation_id': 'test-manual',
        'currency': '643',
        'label': ''
    }
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ WEBHOOK")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Данные: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    print()
    
    try:
        # Отправляем POST запрос
        print("Отправляем POST запрос...")
        response = requests.post(url, data=test_data, timeout=30)
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        print(f"Текст ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ УСПЕХ! Webhook работает корректно")
        else:
            print(f"❌ ОШИБКА! Статус {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ОШИБКА СЕТИ: {e}")
    except Exception as e:
        print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {e}")
    
    print()
    print("=" * 60)
    
    # Тестируем GET запрос
    try:
        print("Тестируем GET запрос...")
        response = requests.get(url, timeout=10)
        print(f"GET статус: {response.status_code}")
        print(f"GET ответ: {response.text}")
    except Exception as e:
        print(f"GET ошибка: {e}")

if __name__ == "__main__":
    test_webhook()
