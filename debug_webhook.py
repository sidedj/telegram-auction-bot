#!/usr/bin/env python3
"""
Отладочный тест webhook'а - проверяем что именно возвращает сервер
"""
import requests
import hashlib
from datetime import datetime

WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"
YOOMONEY_SECRET = "SaTKEuJWPVXJI/JFpXDCHZ4q"

def debug_webhook():
    """Отладочный тест webhook'а"""
    print("🔍 Отладочный тест webhook'а...")
    
    # Простые тестовые данные
    data = {
        'notification_type': 'p2p-incoming',
        'operation_id': f"debug_test_{int(datetime.now().timestamp())}",
        'amount': '50.00',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    
    # Вычисляем подпись
    sorted_keys = sorted(data.keys())
    string_to_sign = "&".join([f"{key}={data[key]}" for key in sorted_keys])
    signature = hashlib.sha1((string_to_sign + YOOMONEY_SECRET).encode('utf-8')).hexdigest()
    data['sha1_hash'] = signature
    
    print(f"📤 Отправляем данные:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(WEBHOOK_URL, data=data, timeout=30)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Тело ответа: {response.text}")
        
        # Проверяем, что возвращает GET запрос
        print(f"\n🔍 Проверяем GET запрос...")
        get_response = requests.get(WEBHOOK_URL, timeout=10)
        print(f"   GET статус: {get_response.status_code}")
        print(f"   GET ответ: {get_response.text}")
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Отладочный тест webhook'а...")
    
    success = debug_webhook()
    
    if success:
        print("\n🎉 Webhook работает!")
    else:
        print("\n⚠️ Webhook не работает.")
