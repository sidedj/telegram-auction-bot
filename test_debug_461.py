#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладочный тест для суммы 461.43₽ - проверяем что именно происходит на сервере
"""

import requests
import json
import time
import hashlib

def test_debug_461():
    """Отладочный тест для суммы 461.43₽"""
    print("🔍 Отладочный тест для суммы 461.43₽")
    print("=" * 60)
    
    # URL основного endpoint
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    # Тестовые данные для суммы 461.43₽
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': f'debug_461_{int(time.time())}',
        'amount': '461.43',
        'withdraw_amount': '461.43',
        'currency': '643',
        'datetime': '2024-01-01T12:00:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    
    # Вычисляем подпись для реалистичности
    sorted_keys = sorted(test_data.keys())
    string_to_sign = "&".join([f"{key}={test_data[key]}" for key in sorted_keys])
    signature = hashlib.sha1((string_to_sign + "SaTKEuJWPVXJI/JFpXDCHZ4q").encode('utf-8')).hexdigest()
    test_data['sha1_hash'] = signature
    
    print(f"📤 Отправляем данные:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 Ожидаемый результат: 0 публикаций")
    print(f"❌ Проблема: пользователь получил 461 публикацию")
    
    try:
        # Отправляем POST запрос
        response = requests.post(url, data=test_data, timeout=30)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook: OK")
            print("💡 Проверьте логи Railway для деталей")
        else:
            print("❌ Webhook: Ошибка")
            
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
        return False

def test_other_problem_amounts():
    """Тестируем другие проблемные суммы"""
    print("\n🔍 Тест других проблемных сумм")
    print("=" * 60)
    
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    # Тестовые случаи с суммами, которые не должны давать публикации
    test_cases = [
        {'amount': '25.00', 'description': '25₽ - пользователь получил 25 публикаций'},
        {'amount': '100.00', 'description': '100₽ - может дать 100 публикаций'},
        {'amount': '300.00', 'description': '300₽ - может дать 300 публикаций'},
        {'amount': '500.00', 'description': '500₽ - может дать 500 публикаций'},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Ожидается: 0 публикаций")
        
        test_data = {
            'notification_type': 'p2p-incoming',
            'operation_id': f'debug_problem_{i}_{int(time.time())}',
            'amount': case['amount'],
            'withdraw_amount': case['amount'],
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
        
        try:
            response = requests.post(url, data=test_data, timeout=30)
            print(f"   📥 Статус: {response.status_code}")
            print(f"   📥 Ответ: {response.text}")
            
            if response.status_code == 200:
                print("   ✅ Webhook: OK")
            else:
                print("   ❌ Webhook: Ошибка")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Отладочный тест проблемных сумм...")
    
    test_debug_461()
    test_other_problem_amounts()
    
    print("\n🎉 Отладочное тестирование завершено!")
    print("\n💡 Если тесты показывают 0 публикаций, но пользователь получил 461,")
    print("   то проблема может быть в:")
    print("   1. Кэшировании старого кода на сервере")
    print("   2. Использовании другого endpoint")
    print("   3. Обработке через другую систему")
    print("   4. Неправильном развертывании изменений")
