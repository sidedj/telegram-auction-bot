#!/usr/bin/env python3
import requests
import json

# Тестируем webhook напрямую
url = "https://telegabot-production-3c68.up.railway.app/yoomoney"

# Тестовые данные как от YooMoney
test_data = {
    'notification_type': 'p2p-incoming',
    'bill_id': '',
    'amount': '100.00',
    'datetime': '2025-09-06T07:20:00Z',
    'codepro': 'false',
    'sender': '41001000040',
    'sha1_hash': 'test_hash',
    'test_notification': 'true',
    'operation_label': '',
    'operation_id': 'test-manual',
    'currency': '643',
    'label': ''
}

print("Отправляем тестовые данные на webhook...")
print(f"URL: {url}")
print(f"Данные: {test_data}")

try:
    response = requests.post(url, data=test_data, timeout=30)
    print(f"Статус ответа: {response.status_code}")
    print(f"Ответ: {response.text}")
except Exception as e:
    print(f"Ошибка: {e}")
