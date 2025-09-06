#!/usr/bin/env python3
"""
Простой тест webhook
"""
import requests
import json

WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"

def test_simple_webhook():
    """Тестирует простой webhook"""
    print("🧪 Тестируем простой webhook...")
    
    # Простые данные
    data = {
        'notification_type': 'card-incoming',
        'operation_id': 'test_simple_123',
        'amount': '50.00'
    }
    
    print(f"📤 Отправляем простые данные:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(WEBHOOK_URL, data=data, timeout=30)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook работает!")
            return True
        else:
            print("❌ Webhook вернул ошибку!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
        return False

def test_get_request():
    """Тестирует GET запрос"""
    print("\n🔍 Тестируем GET запрос...")
    
    try:
        response = requests.get(WEBHOOK_URL, timeout=30)
        
        print(f"📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200 and response.text == "OK":
            print("✅ GET запрос работает!")
            return True
        else:
            print("❌ GET запрос не работает!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при GET запросе: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тестирование простого webhook")
    print("=" * 50)
    
    # Тест GET запроса
    get_success = test_get_request()
    
    # Тест POST запроса
    post_success = test_simple_webhook()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")
    print("=" * 50)
    print(f"GET запрос: {'✅ Успешно' if get_success else '❌ Ошибка'}")
    print(f"POST запрос: {'✅ Успешно' if post_success else '❌ Ошибка'}")
    
    if get_success and post_success:
        print("\n🎉 Webhook работает корректно!")
    else:
        print("\n⚠️ Webhook требует исправлений")
    
    print("\n✨ Тестирование завершено!")
