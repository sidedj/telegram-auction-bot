#!/usr/bin/env python3
"""
Тестовый скрипт для симуляции платежа через YooMoney webhook
"""

import requests
import json
import hashlib
import time

# Настройки
WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"
YOOMONEY_SECRET = "SaTKEuJWPVXJI/JFpXDCHZ4q"
USER_ID = 7647551803  # ID пользователя для тестирования

def create_test_payment(amount=50.00, operation_id=None):
    """Создает тестовые данные платежа"""
    if operation_id is None:
        operation_id = f"test_payment_{int(time.time())}"
    
    # Данные платежа
    payment_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': operation_id,
        'amount': str(amount),
        'currency': '643',
        'datetime': '2025-09-06T08:58:00Z',
        'sender': '4100118987681575',
        'codepro': 'false',
        'unaccepted': 'false',
        'label': f'user_{USER_ID}',
        'test_notification': 'false'  # Реальный платеж
    }
    
    # Добавляем подпись (если нужна)
    if YOOMONEY_SECRET:
        check_string = f"{payment_data['notification_type']}&{payment_data['operation_id']}&{payment_data['amount']}&{payment_data['currency']}&{payment_data['datetime']}&{payment_data['sender']}&{payment_data['codepro']}&{payment_data['label']}&{YOOMONEY_SECRET}"
        sha1_hash = hashlib.sha1(check_string.encode()).hexdigest()
        payment_data['sha1_hash'] = sha1_hash
    
    return payment_data

def test_payment():
    """Тестирует платеж"""
    print("🧪 Тестирование платежа через webhook...")
    
    # Создаем тестовый платеж
    payment_data = create_test_payment(amount=50.00)
    
    print(f"📤 Отправляем данные: {json.dumps(payment_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(
            WEBHOOK_URL,
            data=payment_data,
            timeout=30
        )
        
        print(f"📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Заголовки: {dict(response.headers)}")
        print(f"   Содержимое: {response.text}")
        
        if response.status_code == 200:
            print("✅ Платеж успешно обработан!")
        else:
            print("❌ Ошибка при обработке платежа")
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")

def test_duplicate_payment():
    """Тестирует повторный платеж"""
    print("\n🔄 Тестирование повторного платежа...")
    
    # Используем тот же operation_id
    operation_id = f"duplicate_test_{int(time.time())}"
    
    # Первый платеж
    print("1️⃣ Первый платеж:")
    payment_data1 = create_test_payment(amount=50.00, operation_id=operation_id)
    response1 = requests.post(WEBHOOK_URL, data=payment_data1, timeout=30)
    print(f"   Статус: {response1.status_code}")
    print(f"   Ответ: {response1.text}")
    
    # Второй платеж (дубликат)
    print("2️⃣ Второй платеж (дубликат):")
    payment_data2 = create_test_payment(amount=50.00, operation_id=operation_id)
    response2 = requests.post(WEBHOOK_URL, data=payment_data2, timeout=30)
    print(f"   Статус: {response2.status_code}")
    print(f"   Ответ: {response2.text}")

if __name__ == "__main__":
    print("🚀 Запуск тестирования платежей")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    print(f"👤 User ID: {USER_ID}")
    print("=" * 50)
    
    # Тест обычного платежа
    test_payment()
    
    # Тест повторного платежа
    test_duplicate_payment()
    
    print("\n✅ Тестирование завершено!")
