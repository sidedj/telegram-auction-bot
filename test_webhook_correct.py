#!/usr/bin/env python3
"""
Правильный тест webhook в формате YooMoney
"""
import requests

WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"

def test_webhook_correct():
    """Тестирует webhook в правильном формате"""
    print("🧪 Тестируем webhook в формате YooMoney...")
    
    # Данные в формате application/x-www-form-urlencoded (как YooMoney)
    data = {
        "notification_type": "card-incoming",
        "test_notification": "true",
        "amount": "10.00",
        "currency": "643",
        "label": "test_label"
    }
    
    print(f"📤 Отправляем данные:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    try:
        # Важно использовать data=, а не json=
        response = requests.post(WEBHOOK_URL, data=data, timeout=30)
        
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

def test_webhook_yoomoney_format():
    """Тестирует webhook в точном формате YooMoney"""
    print("\n🔧 Тестируем в формате YooMoney...")
    
    # Данные как от YooMoney
    data = {
        'notification_type': 'card-incoming',
        'operation_id': 'test_operation_123',
        'amount': '48.50',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': '2025-09-06T16:50:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    
    print(f"📤 Отправляем данные YooMoney:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(WEBHOOK_URL, data=data, timeout=30)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook работает с данными YooMoney!")
            return True
        else:
            print("❌ Webhook не работает с данными YooMoney!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Правильный тест webhook")
    print("=" * 50)
    
    # Тест 1: Простые данные
    test1 = test_webhook_correct()
    
    # Тест 2: Данные YooMoney
    test2 = test_webhook_yoomoney_format()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")
    print("=" * 50)
    print(f"Простые данные: {'✅ Успешно' if test1 else '❌ Ошибка'}")
    print(f"Данные YooMoney: {'✅ Успешно' if test2 else '❌ Ошибка'}")
    
    if test1 or test2:
        print("\n🎉 Webhook работает!")
    else:
        print("\n⚠️ Webhook не работает")
    
    print("\n✨ Тестирование завершено!")
