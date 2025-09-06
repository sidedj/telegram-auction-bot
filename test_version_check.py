#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка версии кода на сервере
"""

import requests
import json
import time
import hashlib

def test_version_check():
    """Проверяем какая версия кода работает на сервере"""
    print("🔍 Проверка версии кода на сервере")
    print("=" * 60)
    
    # URL основного endpoint
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    # Тестовые данные для суммы 25₽ (должна давать 0 публикаций)
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': f'version_check_{int(time.time())}',
        'amount': '25.00',
        'withdraw_amount': '25.00',
        'currency': '643',
        'datetime': '2024-01-01T12:00:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    
    # Вычисляем подпись
    sorted_keys = sorted(test_data.keys())
    string_to_sign = "&".join([f"{key}={test_data[key]}" for key in sorted_keys])
    signature = hashlib.sha1((string_to_sign + "SaTKEuJWPVXJI/JFpXDCHZ4q").encode('utf-8')).hexdigest()
    test_data['sha1_hash'] = signature
    
    print(f"📤 Тестируем сумму 25₽")
    print(f"🎯 Ожидается: 0 публикаций (новая версия)")
    print(f"❌ Если получим 25 публикаций - работает старая версия")
    
    try:
        response = requests.post(url, data=test_data, timeout=30)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook: OK")
            
            # Проверяем логику
            if "25 публикаций" in str(test_data):
                print("❌ ПРОБЛЕМА: На сервере работает СТАРАЯ версия кода!")
                print("   Сумма 25₽ дает 25 публикаций вместо 0")
                print("   Нужно принудительно перезапустить Railway")
            else:
                print("✅ На сервере работает НОВАЯ версия кода")
        else:
            print("❌ Webhook: Ошибка")
            
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
        return False

def test_health_endpoint():
    """Проверяем health endpoint"""
    print("\n🔍 Проверка health endpoint")
    print("-" * 40)
    
    try:
        response = requests.get("https://web-production-fa7dc.up.railway.app/health", timeout=10)
        print(f"📥 Health статус: {response.status_code}")
        print(f"📥 Health ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Сервер работает")
        else:
            print("❌ Проблема с сервером")
            
    except Exception as e:
        print(f"❌ Ошибка health check: {e}")

if __name__ == "__main__":
    print("🚀 Проверка версии кода на сервере...")
    
    test_health_endpoint()
    test_version_check()
    
    print("\n" + "=" * 60)
    print("💡 Рекомендации:")
    print("   1. Если тест показывает 25 публикаций за 25₽ - код не обновился")
    print("   2. Нужно принудительно перезапустить Railway")
    print("   3. Или проверить логи развертывания в Railway Dashboard")
    print("   4. Возможно, есть проблема с автодеплоем")
