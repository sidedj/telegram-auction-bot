#!/usr/bin/env python3
"""
Локальный тест webhook'а - проверяем код без отправки на сервер
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import yoomoney_webhook
from flask import Flask, request
import threading
import time

# Создаем тестовое Flask приложение
app = Flask(__name__)

def test_webhook_locally():
    """Тестирует webhook локально"""
    print("🧪 Тестирование webhook'а локально...")
    
    # Тестовые данные
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': 'test_notification_local',
        'amount': '345.98',
        'withdraw_amount': '50.00',
        'currency': '643',
        'datetime': '2025-09-06T16:05:55.538068Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    
    print(f"📤 Тестовые данные:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    # Симулируем POST запрос
    with app.test_request_context('/yoomoney', method='POST', data=test_data):
        try:
            result = yoomoney_webhook()
            print(f"\n📥 Результат: {result}")
            print("✅ Webhook работает локально!")
            return True
        except Exception as e:
            print(f"\n❌ Ошибка в webhook: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

if __name__ == "__main__":
    print("🚀 Локальное тестирование webhook'а...")
    
    success = test_webhook_locally()
    
    if success:
        print("\n🎉 Webhook работает правильно локально!")
        print("💡 Проблема в том, что на сервере запущена старая версия кода")
    else:
        print("\n⚠️ Webhook требует исправлений.")
