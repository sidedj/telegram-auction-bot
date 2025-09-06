#!/usr/bin/env python3
"""
Тест исправленного webhook'а - проверяем обработку тестовых уведомлений
"""
import requests
import hashlib
from datetime import datetime

WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"
YOOMONEY_SECRET = "SaTKEuJWPVXJI/JFpXDCHZ4q"

def calculate_signature(data, secret):
    """Вычисляет подпись для данных"""
    # Сортируем ключи по алфавиту
    sorted_keys = sorted(data.keys())
    
    # Создаем строку для подписи
    string_to_sign = "&".join([f"{key}={data[key]}" for key in sorted_keys if key != 'sha1_hash'])
    
    # Вычисляем HMAC-SHA1
    signature = hashlib.sha1((string_to_sign + secret).encode('utf-8')).hexdigest()
    
    return signature

def test_webhook_fixed():
    """Тестирует исправленный webhook"""
    print("🔧 Тестирование ИСПРАВЛЕННОГО webhook'а...")
    
    # Тестовые данные как от ЮMoney
    data = {
        'notification_type': 'p2p-incoming',
        'operation_id': f"test_notification_{int(datetime.now().timestamp())}",
        'amount': '345.98',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',  # Админ
        'test_notification': 'true'
    }
    
    # Вычисляем подпись
    signature = calculate_signature(data, YOOMONEY_SECRET)
    data['sha1_hash'] = signature
    
    print(f"📤 Отправляем тестовые данные:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔐 Подпись: {signature}")
    
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
    print("🚀 Тестирование ИСПРАВЛЕННОГО webhook'а...")
    
    success = test_webhook_fixed()
    
    if success:
        print("\n🎉 Webhook работает правильно!")
        print("💡 Если в логах все еще видно 'пропускаем', значит на сервере старая версия кода")
    else:
        print("\n⚠️ Webhook требует исправлений.")
