#!/usr/bin/env python3
"""
Простой тест webhook
"""
import requests

WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"

def test_webhook():
    """Тестирует webhook"""
    print("🧪 Тестируем webhook...")
    
    # Простые данные
    data = {
        'test': 'value'
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=data, timeout=30)
        
        print(f"📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
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
    print("🚀 Тест webhook")
    test_webhook()