#!/usr/bin/env python3
# Файл: test_webhook.py

"""
Скрипт для тестирования webhook ЮMoney
"""

import requests
import json
from config import YOOMONEY_SECRET

def test_local_webhook():
    """Тестирует локальный webhook"""
    url = "http://localhost:8080/yoomoney"
    
    # Тестовые данные
    test_data = {
        "notification_secret": YOOMONEY_SECRET,
        "label": "user_123456",
        "amount": "50.00",
        "operation_id": "test_12345",
        "unaccepted": "false"
    }
    
    print("🧪 Тестирование локального webhook...")
    print(f"📡 URL: {url}")
    print(f"📦 Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, data=test_data, timeout=10)
        print(f"✅ Статус: {response.status_code}")
        print(f"📄 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("🎉 Webhook работает корректно!")
        else:
            print("❌ Webhook вернул ошибку")
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Не удается подключиться к серверу")
        print("💡 Убедитесь, что сервер платежей запущен: python start_payment_server.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_ngrok_webhook(ngrok_url):
    """Тестирует webhook через ngrok"""
    url = f"{ngrok_url}/yoomoney"
    
    # Тестовые данные
    test_data = {
        "notification_secret": YOOMONEY_SECRET,
        "label": "user_123456",
        "amount": "50.00",
        "operation_id": "test_ngrok_12345",
        "unaccepted": "false"
    }
    
    print(f"🧪 Тестирование ngrok webhook...")
    print(f"📡 URL: {url}")
    print(f"📦 Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, data=test_data, timeout=10)
        print(f"✅ Статус: {response.status_code}")
        print(f"📄 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("🎉 Ngrok webhook работает корректно!")
        else:
            print("❌ Ngrok webhook вернул ошибку")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def check_server_status():
    """Проверяет статус сервера"""
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Сервер работает: {data}")
            return True
        else:
            print(f"❌ Сервер вернул ошибку: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки сервера: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Тестирование webhook ЮMoney")
    print("=" * 50)
    
    # Проверяем статус сервера
    if not check_server_status():
        print("\n💡 Для запуска сервера выполните:")
        print("   python start_payment_server.py")
        exit(1)
    
    print("\n" + "=" * 50)
    
    # Тестируем локальный webhook
    test_local_webhook()
    
    print("\n" + "=" * 50)
    print("📝 Для тестирования через ngrok:")
    print("1. Запустите ngrok: ngrok http 5000")
    print("2. Скопируйте URL (например: https://abc123.ngrok.io)")
    print("3. Запустите: python test_webhook.py https://abc123.ngrok.io")
    
    # Если передан URL ngrok, тестируем его
    import sys
    if len(sys.argv) > 1:
        ngrok_url = sys.argv[1]
        if ngrok_url.startswith("http"):
            print(f"\n🧪 Тестирование ngrok URL: {ngrok_url}")
            test_ngrok_webhook(ngrok_url)
        else:
            print("❌ Неверный формат URL. Используйте: https://abc123.ngrok.io")
