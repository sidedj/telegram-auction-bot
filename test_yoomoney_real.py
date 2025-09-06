#!/usr/bin/env python3
import requests
import json

def test_yoomoney_real():
    """Тестирует webhook с реальными данными YooMoney"""
    
    url = "https://telegabot-production-3c68.up.railway.app/yoomoney"
    
    # Реальные данные YooMoney (тестовые)
    real_data = {
        'notification_type': 'p2p-incoming',
        'bill_id': 'test-bill-123',
        'amount': '500.00',
        'datetime': '2025-09-06T10:35:00Z',
        'codepro': 'false',
        'sender': '41001000040',
        'sha1_hash': 'real_test_hash_12345',
        'test_notification': 'true',
        'operation_label': 'test-payment',
        'operation_id': 'test-real-12345',
        'currency': '643',
        'label': 'test-label'
    }
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ С РЕАЛЬНЫМИ ДАННЫМИ YOOMONEY")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Данные: {json.dumps(real_data, indent=2, ensure_ascii=False)}")
    print()
    
    try:
        # Отправляем POST запрос
        print("Отправляем POST запрос...")
        response = requests.post(url, data=real_data, timeout=30)
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        print(f"Текст ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ УСПЕХ! Webhook обработал данные YooMoney корректно")
        else:
            print(f"❌ ОШИБКА! Статус {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ОШИБКА СЕТИ: {e}")
    except Exception as e:
        print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {e}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_yoomoney_real()
