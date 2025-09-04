#!/usr/bin/env python3
# Файл: check_router_setup.py

"""
Скрипт для проверки настройки проброса портов в роутере
"""

import requests
import socket
import time
from datetime import datetime

def check_local_server():
    """Проверяет, что локальный сервер работает"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Локальный сервер работает")
            return True
        else:
            print(f"❌ Локальный сервер вернул ошибку: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Локальный сервер не работает: {e}")
        return False

def check_external_access():
    """Проверяет доступность сервера из интернета"""
    external_ip = "212.111.81.230"
    port = 5000
    
    print(f"🔍 Проверяем доступность {external_ip}:{port}...")
    
    try:
        # Проверяем подключение к порту
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((external_ip, port))
        sock.close()
        
        if result == 0:
            print("✅ Порт доступен из интернета")
            
            # Проверяем HTTP ответ
            try:
                response = requests.get(f"http://{external_ip}:{port}/health", timeout=10)
                if response.status_code == 200:
                    print("✅ HTTP сервис работает")
                    return True
                else:
                    print(f"❌ HTTP сервис вернул ошибку: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ HTTP запрос не прошел: {e}")
                return False
        else:
            print("❌ Порт недоступен из интернета")
            print("💡 Нужно настроить проброс портов в роутере")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def test_webhook():
    """Тестирует webhook"""
    external_ip = "212.111.81.230"
    port = 5000
    
    print(f"🧪 Тестируем webhook на {external_ip}:{port}...")
    
    test_data = {
        "notification_secret": "SaTKEuJWPVXJl/JFpXDCHZ4q",
        "label": "user_123456",
        "amount": "50.00",
        "operation_id": "test_router_12345",
        "unaccepted": "false"
    }
    
    try:
        response = requests.post(
            f"http://{external_ip}:{port}/yoomoney",
            data=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Webhook работает корректно!")
            print("🎉 Проброс портов настроен правильно!")
            return True
        else:
            print(f"❌ Webhook вернул ошибку: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования webhook: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🔧 Проверка настройки проброса портов")
    print("=" * 50)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Шаг 1: Проверяем локальный сервер
    print("📋 Шаг 1: Проверка локального сервера")
    if not check_local_server():
        print("💡 Запустите сервер: python start_payment_server.py")
        return
    print()
    
    # Шаг 2: Проверяем доступность из интернета
    print("📋 Шаг 2: Проверка доступности из интернета")
    if not check_external_access():
        print("💡 Настройте проброс портов в роутере")
        print("📖 Инструкция: ROUTER_SETUP_GUIDE.md")
        return
    print()
    
    # Шаг 3: Тестируем webhook
    print("📋 Шаг 3: Тестирование webhook")
    if test_webhook():
        print()
        print("🎉 ВСЕ ГОТОВО!")
        print("✅ Проброс портов настроен")
        print("✅ Сервер доступен из интернета")
        print("✅ Webhook работает")
        print()
        print("🔧 Теперь настройте ЮMoney:")
        print("   URL: http://212.111.81.230:5000/yoomoney")
        print("   Секрет: SaTKEuJWPVXJl/JFpXDCHZ4q")
    else:
        print("❌ Webhook не работает")
        print("💡 Проверьте настройки сервера платежей")

if __name__ == "__main__":
    main()
