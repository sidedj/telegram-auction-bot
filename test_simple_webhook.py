#!/usr/bin/env python3
"""
Тест упрощенного webhook'а
"""
import requests
import hashlib
from datetime import datetime

WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"

def test_simple_webhook():
    """Тестирует упрощенный webhook"""
    print("🧪 Тестирование упрощенного webhook'а...")
    
    # Простые данные как от ЮMoney
    data = {
        'operation_id': f"test_simple_{int(datetime.now().timestamp())}",
        'amount': '50',
        'label': 'user_7647551803',
        'sender': '7647551803'
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
            print("❌ Webhook возвращает ошибку!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тестирование упрощенного webhook'а...")
    
    success = test_simple_webhook()
    
    if success:
        print("\n🎉 Webhook работает правильно!")
    else:
        print("\n⚠️ Webhook требует исправлений.")
