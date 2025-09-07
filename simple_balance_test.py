#!/usr/bin/env python3
import requests
import time
import hashlib

# Простой тест баланса
url = "https://web-production-fa7dc.up.railway.app/yoomoney"
user_id = 476589798

test_data = {
    'notification_type': 'p2p-incoming',
    'operation_id': f'simple_test_{int(time.time())}',
    'amount': '50.00',
    'withdraw_amount': '50.00',
    'currency': '643',
    'datetime': '2024-01-01T12:00:00.000Z',
    'sender': '41001000040',
    'codepro': 'false',
    'label': f'user_{user_id}',
    'test_notification': 'true'
}

# Вычисляем подпись
sorted_keys = sorted(test_data.keys())
string_to_sign = "&".join([f"{key}={test_data[key]}" for key in sorted_keys])
signature = hashlib.sha1((string_to_sign + "SaTKEuJWPVXJI/JFpXDCHZ4q").encode('utf-8')).hexdigest()
test_data['sha1_hash'] = signature

print("Отправляем тест пополнения...")
response = requests.post(url, data=test_data, timeout=30)
print(f"Статус: {response.status_code}")
print(f"Ответ: {response.text}")
print("Проверьте баланс в боте!")
