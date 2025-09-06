#!/usr/bin/env python3
"""
Тест обновления баланса через webhook
"""
import requests
import hashlib
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"
YOOMONEY_SECRET = "SaTKEuJWPVXJI/JFpXDCHZ4q"

def calculate_signature(data, secret):
    """Вычисляет подпись для данных"""
    sorted_keys = sorted(data.keys())
    string_to_sign = "&".join([f"{key}={data[key]}" for key in sorted_keys if key != 'sha1_hash'])
    signature = hashlib.sha1((string_to_sign + secret).encode('utf-8')).hexdigest()
    return signature

def test_balance_update():
    """Тестирует обновление баланса через webhook"""
    print("💰 Тестируем обновление баланса...")
    
    # Тестовые данные
    data = {
        'notification_type': 'card-incoming',
        'operation_id': f"test_balance_update_{int(datetime.now().timestamp())}",
        'amount': '48.50',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',  # ID админа для тестирования
        'test_notification': 'true'
    }
    
    # Вычисляем подпись
    signature = calculate_signature(data, YOOMONEY_SECRET)
    data['sha1_hash'] = signature
    
    print(f"📤 Отправляем данные:")
    for key, value in data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(WEBHOOK_URL, data=data, timeout=30)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook обработан успешно!")
            print("💡 Проверьте баланс пользователя в боте командой /stats")
            return True
        else:
            print("❌ Webhook вернул ошибку!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
        return False

def test_multiple_payments():
    """Тестирует несколько платежей подряд"""
    print("\n🔄 Тестируем несколько платежей...")
    
    results = []
    
    # Тест 1: Платеж 50₽ (1 публикация)
    print("\n1️⃣ Платеж 50₽...")
    data1 = {
        'notification_type': 'card-incoming',
        'operation_id': f"test_50_{int(datetime.now().timestamp())}",
        'amount': '48.50',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    data1['sha1_hash'] = calculate_signature(data1, YOOMONEY_SECRET)
    
    try:
        response1 = requests.post(WEBHOOK_URL, data=data1, timeout=30)
        results.append(response1.status_code == 200)
        print(f"   Результат: {'✅ Успешно' if results[-1] else '❌ Ошибка'}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        results.append(False)
    
    # Тест 2: Платеж 200₽ (5 публикаций)
    print("\n2️⃣ Платеж 200₽...")
    data2 = {
        'notification_type': 'card-incoming',
        'operation_id': f"test_200_{int(datetime.now().timestamp())}",
        'amount': '192.00',
        'withdraw_amount': '200.00',
        'currency': '643',
        'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    data2['sha1_hash'] = calculate_signature(data2, YOOMONEY_SECRET)
    
    try:
        response2 = requests.post(WEBHOOK_URL, data=data2, timeout=30)
        results.append(response2.status_code == 200)
        print(f"   Результат: {'✅ Успешно' if results[-1] else '❌ Ошибка'}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        results.append(False)
    
    # Тест 3: Платеж 350₽ (10 публикаций)
    print("\n3️⃣ Платеж 350₽...")
    data3 = {
        'notification_type': 'card-incoming',
        'operation_id': f"test_350_{int(datetime.now().timestamp())}",
        'amount': '322.00',
        'withdraw_amount': '350.00',
        'currency': '643',
        'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    data3['sha1_hash'] = calculate_signature(data3, YOOMONEY_SECRET)
    
    try:
        response3 = requests.post(WEBHOOK_URL, data=data3, timeout=30)
        results.append(response3.status_code == 200)
        print(f"   Результат: {'✅ Успешно' if results[-1] else '❌ Ошибка'}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        results.append(False)
    
    print(f"\n📊 Результаты тестирования:")
    print(f"   Успешных: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 Все платежи обработаны успешно!")
        print("💡 Ожидаемый баланс: 16 публикаций (1+5+10)")
    else:
        print("⚠️ Некоторые платежи не обработаны")
    
    return all(results)

if __name__ == "__main__":
    print("🚀 Тестирование обновления баланса")
    print("=" * 50)
    
    # Тест одного платежа
    success1 = test_balance_update()
    
    # Тест нескольких платежей
    success2 = test_multiple_payments()
    
    print("\n" + "=" * 50)
    print("📋 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 50)
    print(f"Одиночный платеж: {'✅ Успешно' if success1 else '❌ Ошибка'}")
    print(f"Множественные платежи: {'✅ Успешно' if success2 else '❌ Ошибка'}")
    
    if success1 and success2:
        print("\n🎉 Все тесты прошли успешно!")
        print("💡 Проверьте баланс в боте командой /stats")
    else:
        print("\n⚠️ Некоторые тесты не прошли")
        print("💡 Проверьте логи сервера для диагностики")
    
    print("\n✨ Тестирование завершено!")
