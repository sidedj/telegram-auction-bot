#!/usr/bin/env python3
import requests
import time

def test_local_webhook():
    """Тестирует локальный webhook"""
    
    # Ждем немного, чтобы сервер запустился
    time.sleep(2)
    
    url = "http://localhost:8080/yoomoney"
    
    # Тестовые данные
    test_data = {
        'notification_type': 'p2p-incoming',
        'amount': '100.00',
        'test_notification': 'true',
        'operation_id': 'test-local'
    }
    
    print("Тестируем локальный webhook...")
    print(f"URL: {url}")
    
    try:
        # Тестируем POST
        response = requests.post(url, data=test_data, timeout=5)
        print(f"POST статус: {response.status_code}")
        print(f"POST ответ: {response.text}")
        
        # Тестируем GET
        response = requests.get(url, timeout=5)
        print(f"GET статус: {response.status_code}")
        print(f"GET ответ: {response.text}")
        
        # Тестируем health
        response = requests.get("http://localhost:8080/health", timeout=5)
        print(f"Health статус: {response.status_code}")
        print(f"Health ответ: {response.text}")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_local_webhook()
