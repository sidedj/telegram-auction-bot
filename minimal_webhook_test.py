#!/usr/bin/env python3
"""
Минимальный тест webhook
"""
import requests

WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"

def test_minimal_data():
    """Тестирует с минимальными данными"""
    print("🧪 Тестируем с минимальными данными...")
    
    # Минимальные данные
    data = {
        'notification_type': 'card-incoming',
        'operation_id': 'test_minimal_123',
        'amount': '50.00',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': '2025-09-06T16:45:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    
    print(f"📤 Отправляем данные:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(WEBHOOK_URL, data=data, timeout=30)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        print(f"   Заголовки: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Webhook работает!")
            return True
        else:
            print("❌ Webhook вернул ошибку!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
        return False

def test_without_signature():
    """Тестирует без подписи"""
    print("\n🔓 Тестируем без подписи...")
    
    data = {
        'notification_type': 'card-incoming',
        'operation_id': 'test_no_sig_123',
        'amount': '50.00',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': '2025-09-06T16:45:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=data, timeout=30)
        
        print(f"📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook работает без подписи!")
            return True
        else:
            print("❌ Webhook не работает без подписи!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Минимальный тест webhook")
    print("=" * 50)
    
    # Тест с минимальными данными
    test1 = test_minimal_data()
    
    # Тест без подписи
    test2 = test_without_signature()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")
    print("=" * 50)
    print(f"Минимальные данные: {'✅ Успешно' if test1 else '❌ Ошибка'}")
    print(f"Без подписи: {'✅ Успешно' if test2 else '❌ Ошибка'}")
    
    if test1 or test2:
        print("\n🎉 Webhook работает!")
    else:
        print("\n⚠️ Webhook не работает")
    
    print("\n✨ Тестирование завершено!")
