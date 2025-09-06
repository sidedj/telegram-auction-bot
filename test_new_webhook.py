#!/usr/bin/env python3
import requests
import hashlib
import hmac

def create_test_signature(data, secret):
    """Создает тестовую подпись для проверки"""
    string_to_sign = f"{data['notification_type']}&{data['operation_id']}&{data['amount']}&{data['currency']}&{data['datetime']}&{data['sender']}&{data['codepro']}&{secret}&{data['label']}"
    return hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()

def test_new_webhook():
    """Тестирует новый webhook с проверкой подписи"""
    
    url = "http://localhost:8080/yoomoney"
    secret = "SaTKEuJWPVXJl/JFpXDCHZ4q"
    
    # Тестовые данные
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': 'test-operation-123',
        'amount': '100.00',
        'currency': '643',
        'datetime': '2025-09-06T10:40:00Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': '476589798',  # ID пользователя
        'test_notification': 'true'
    }
    
    # Создаем подпись
    signature = create_test_signature(test_data, secret)
    test_data['sha1_hash'] = signature
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ НОВОГО WEBHOOK С ПРОВЕРКОЙ ПОДПИСИ")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Подпись: {signature}")
    print()
    
    try:
        # Тестируем POST запрос
        print("Отправляем POST запрос...")
        response = requests.post(url, data=test_data, timeout=10)
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Текст ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ УСПЕХ! Webhook работает с проверкой подписи")
        else:
            print(f"❌ ОШИБКА! Статус {response.status_code}")
            
        # Тестируем GET запрос
        print("\nТестируем GET запрос...")
        response = requests.get(url, timeout=5)
        print(f"GET статус: {response.status_code}")
        print(f"GET ответ: {response.text}")
        
        # Тестируем health check
        print("\nТестируем health check...")
        response = requests.get("http://localhost:8080/health", timeout=5)
        print(f"Health статус: {response.status_code}")
        print(f"Health ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")

if __name__ == "__main__":
    test_new_webhook()
