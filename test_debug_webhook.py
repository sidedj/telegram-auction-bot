#!/usr/bin/env python3
"""
Тест отладочного webhook'а
"""
import requests
import hashlib
from datetime import datetime

DEBUG_WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney_debug"
YOOMONEY_SECRET = "SaTKEuJWPVXJI/JFpXDCHZ4q"

def test_debug_webhook():
    """Тестирует отладочный webhook"""
    print("🔍 Тест отладочного webhook'а...")
    
    # Тестовые данные
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
    
    print(f"📤 Отправляем данные в отладочный webhook:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(DEBUG_WEBHOOK_URL, data=data, timeout=30)
        
        print(f"\n📥 Ответ отладочного webhook'а:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тест отладочного webhook'а...")
    
    success = test_debug_webhook()
    
    if success:
        print("\n🎉 Отладочный webhook работает!")
    else:
        print("\n⚠️ Отладочный webhook не работает.")
