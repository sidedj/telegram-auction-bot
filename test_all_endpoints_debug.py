#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладочный тест всех endpoints для суммы 461.43₽
"""

import requests
import json
import time
import hashlib

def test_endpoint_with_debug(endpoint, amount, description):
    """Тестируем endpoint с отладочной информацией"""
    print(f"\n🔍 {description}")
    print(f"   Endpoint: {endpoint}")
    print(f"   Сумма: {amount}₽")
    print("-" * 60)
    
    url = f"https://web-production-fa7dc.up.railway.app{endpoint}"
    
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': f'debug_{endpoint.replace("/", "_")}_{int(time.time())}',
        'amount': str(amount),
        'withdraw_amount': str(amount),
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
    
    print(f"📤 Отправляем данные:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 Ожидаемый результат: 0 публикаций")
    print(f"❌ Проблема: пользователь получил {int(amount)} публикаций")
    
    try:
        response = requests.post(url, data=test_data, timeout=30)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook: OK")
        else:
            print("❌ Webhook: Ошибка")
            
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_all_endpoints():
    """Тестируем все endpoints"""
    print("🚀 Отладочный тест всех endpoints")
    print("=" * 80)
    
    # Тестируем все endpoints с проблемной суммой
    endpoints = [
        ('/yoomoney', 'Основной YooMoney endpoint'),
        ('/webhook', 'Новый webhook endpoint'),
        ('/yoomoney_debug', 'Отладочный endpoint')
    ]
    
    amount = 461.43
    
    for endpoint, description in endpoints:
        test_endpoint_with_debug(endpoint, amount, description)
    
    print(f"\n🔍 Тестируем также другие проблемные суммы")
    print("=" * 80)
    
    # Тестируем другие проблемные суммы
    problem_amounts = [25.0, 100.0, 300.0, 500.0]
    
    for amount in problem_amounts:
        test_endpoint_with_debug('/yoomoney', amount, f'YooMoney endpoint с суммой {amount}₽')

if __name__ == "__main__":
    test_all_endpoints()
    
    print("\n" + "=" * 80)
    print("🎉 Отладочное тестирование завершено!")
    print("\n💡 Анализ:")
    print("   - Если все тесты показывают 0 публикаций, но пользователь получил 461,")
    print("     то проблема в развертывании изменений на сервере")
    print("   - Если какой-то тест показывает неправильный результат,")
    print("     то проблема в конкретном endpoint")
    print("   - Проверьте логи Railway для деталей")
