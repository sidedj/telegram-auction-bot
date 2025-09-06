#!/usr/bin/env python3
import requests
import hashlib

def create_test_signature(data, secret):
    """Создает тестовую подпись для проверки"""
    string_to_sign = f"{data['notification_type']}&{data['operation_id']}&{data['amount']}&{data['currency']}&{data['datetime']}&{data['sender']}&{data['codepro']}&{secret}&{data['label']}"
    return hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()

def test_user_format():
    """Тестирует webhook с форматом user_123456789"""
    
    url = "https://telegabot-production-3c68.up.railway.app/yoomoney"
    secret = "SaTKEuJWPVXJl/JFpXDCHZ4q"
    
    # Тестовые данные с форматом user_123456789
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': 'test-user-format-123',
        'amount': '100.00',
        'currency': '643',
        'datetime': '2025-09-06T10:50:00Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',  # Формат user_123456789
        'test_notification': 'true'
    }
    
    # Создаем подпись
    signature = create_test_signature(test_data, secret)
    test_data['sha1_hash'] = signature
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ WEBHOOK С ФОРМАТОМ user_123456789")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Label: {test_data['label']}")
    print(f"User ID: 476589798 (извлеченный из label)")
    print(f"Сумма: {test_data['amount']} руб.")
    print(f"Подпись: {signature}")
    print()
    
    try:
        # Тестируем POST запрос
        print("Отправляем POST запрос...")
        response = requests.post(url, data=test_data, timeout=30)
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Текст ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ УСПЕХ! Webhook корректно обработал формат user_123456789")
        else:
            print(f"❌ ОШИБКА! Статус {response.status_code}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")

if __name__ == "__main__":
    test_user_format()
