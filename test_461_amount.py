#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для суммы 461.43₽ - должна давать 0 публикаций
"""

import requests
import json
import time

def test_461_amount():
    """Тестируем сумму 461.43₽"""
    print("🧪 Тест суммы 461.43₽")
    print("=" * 50)
    
    # URL основного endpoint
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    # Тестовые данные для суммы 461.43₽
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': f'test_461_{int(time.time())}',
        'amount': '461.43',
        'withdraw_amount': '461.43',
        'currency': '643',
        'datetime': '2024-01-01T12:00:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    
    print(f"📤 Отправляем данные:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 Ожидаемый результат: 0 публикаций (сумма не соответствует тарифам)")
    
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

def test_other_amounts():
    """Тестируем другие проблемные суммы"""
    print("\n🔍 Тест других проблемных сумм")
    print("=" * 50)
    
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    # Тестовые случаи с суммами, которые не должны давать публикации
    test_cases = [
        {'amount': '25.00', 'expected': 0, 'description': '25₽ = 0 публикаций'},
        {'amount': '100.00', 'expected': 0, 'description': '100₽ = 0 публикаций'},
        {'amount': '300.00', 'expected': 0, 'description': '300₽ = 0 публикаций'},
        {'amount': '500.00', 'expected': 0, 'description': '500₽ = 0 публикаций'},
        {'amount': '1000.00', 'expected': 0, 'description': '1000₽ = 0 публикаций'},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Ожидается: {case['expected']} публикаций")
        
        test_data = {
            'notification_type': 'p2p-incoming',
            'operation_id': f'test_problem_{i}_{int(time.time())}',
            'amount': case['amount'],
            'withdraw_amount': case['amount'],
            'currency': '643',
            'datetime': '2024-01-01T12:00:00.000Z',
            'sender': '41001000040',
            'codepro': 'false',
            'label': 'user_476589798',
            'test_notification': 'true'
        }
        
        try:
            response = requests.post(url, data=test_data, timeout=30)
            if response.status_code == 200:
                print("   ✅ Webhook: OK")
            else:
                print("   ❌ Webhook: Ошибка")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Тест проблемных сумм...")
    
    test_461_amount()
    test_other_amounts()
    
    print("\n🎉 Тестирование завершено!")
