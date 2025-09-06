#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест всех webhook endpoints для суммы 461.43₽
"""

import requests
import json
import time

def test_endpoint(endpoint, amount):
    """Тестируем конкретный endpoint"""
    print(f"\n🔍 Тестируем {endpoint} с суммой {amount}₽")
    print("-" * 40)
    
    url = f"https://web-production-fa7dc.up.railway.app{endpoint}"
    
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': f'test_{endpoint.replace("/", "_")}_{int(time.time())}',
        'amount': str(amount),
        'withdraw_amount': str(amount),
        'currency': '643',
        'datetime': '2024-01-01T12:00:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798',
        'test_notification': 'true'
    }
    
    print(f"📤 URL: {url}")
    print(f"📤 Сумма: {amount}₽")
    print(f"🎯 Ожидается: 0 публикаций")
    
    try:
        response = requests.post(url, data=test_data, timeout=30)
        print(f"📥 Статус: {response.status_code}")
        print(f"📥 Ответ: {response.text}")
        
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
    print("🚀 Тест всех webhook endpoints")
    print("=" * 60)
    
    endpoints = ['/yoomoney', '/webhook', '/yoomoney_debug']
    amount = 461.43
    
    for endpoint in endpoints:
        test_endpoint(endpoint, amount)
    
    print(f"\n🔍 Тестируем также другие проблемные суммы на /webhook")
    print("-" * 60)
    
    # Тестируем /webhook с разными суммами
    problem_amounts = [25.0, 100.0, 300.0, 500.0, 461.43]
    
    for amount in problem_amounts:
        test_endpoint('/webhook', amount)

if __name__ == "__main__":
    test_all_endpoints()
    print("\n🎉 Тестирование всех endpoints завершено!")
