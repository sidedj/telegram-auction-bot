#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест учета комиссии YooMoney
"""

import requests
import json
import time

def test_commission():
    """Тестируем учет комиссии YooMoney"""
    print("🧪 Тест учета комиссии YooMoney")
    print("=" * 50)
    
    # URL webhook
    url = "https://web-production-fa7dc.up.railway.app/webhook"
    
    # Тестовые случаи с разными комиссиями
    test_cases = [
        {
            'name': '50₽ без комиссии',
            'amount': '50.00',
            'withdraw_amount': '50.00',
            'expected_publications': 1
        },
        {
            'name': '50₽ с комиссией 4₽',
            'amount': '54.00',
            'withdraw_amount': '50.00',
            'expected_publications': 1
        },
        {
            'name': '200₽ без комиссии',
            'amount': '200.00',
            'withdraw_amount': '200.00',
            'expected_publications': 4
        },
        {
            'name': '200₽ с комиссией 16₽',
            'amount': '216.00',
            'withdraw_amount': '200.00',
            'expected_publications': 4
        },
        {
            'name': '350₽ без комиссии',
            'amount': '350.00',
            'withdraw_amount': '350.00',
            'expected_publications': 7
        },
        {
            'name': '350₽ с комиссией 28₽',
            'amount': '378.00',
            'withdraw_amount': '350.00',
            'expected_publications': 7
        },
        {
            'name': 'Слишком маленькая сумма',
            'amount': '30.00',
            'withdraw_amount': '30.00',
            'expected_publications': 0
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        print(f"   Сумма: {case['amount']}₽ → {case['withdraw_amount']}₽")
        print(f"   Ожидается: {case['expected_publications']} публикаций")
        
        # Данные платежа
        payment_data = {
            'notification_type': 'card-incoming',
            'operation_id': f'test_commission_{i}',
            'amount': case['amount'],
            'withdraw_amount': case['withdraw_amount'],
            'currency': '643',
            'datetime': '2025-09-06T18:00:00.000Z',
            'sender': '41001000040',
            'codepro': 'false',
            'label': 'user_476589798'
        }
        
        try:
            # Отправляем запрос
            response = requests.post(url, data=payment_data, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Webhook: OK")
                print(f"   💡 Проверьте логи Railway для деталей")
            else:
                print(f"   ❌ Webhook: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Небольшая пауза между запросами
        time.sleep(1)

def test_commission_ranges():
    """Тестируем граничные значения комиссии"""
    print("\n🔍 Тест граничных значений комиссии")
    print("=" * 50)
    
    # Граничные значения для каждого тарифа
    boundary_tests = [
        # Тариф 50₽ (46-54₽)
        {'amount': '46.00', 'withdraw_amount': '46.00', 'expected': 1, 'desc': '50₽ минимум'},
        {'amount': '54.00', 'withdraw_amount': '54.00', 'expected': 1, 'desc': '50₽ максимум'},
        {'amount': '45.00', 'withdraw_amount': '45.00', 'expected': 0, 'desc': '50₽ слишком мало'},
        {'amount': '55.00', 'withdraw_amount': '55.00', 'expected': 0, 'desc': '50₽ слишком много'},
        
        # Тариф 200₽ (184-216₽)
        {'amount': '184.00', 'withdraw_amount': '184.00', 'expected': 4, 'desc': '200₽ минимум'},
        {'amount': '216.00', 'withdraw_amount': '216.00', 'expected': 4, 'desc': '200₽ максимум'},
        {'amount': '183.00', 'withdraw_amount': '183.00', 'expected': 0, 'desc': '200₽ слишком мало'},
        {'amount': '217.00', 'withdraw_amount': '217.00', 'expected': 0, 'desc': '200₽ слишком много'},
    ]
    
    for test in boundary_tests:
        print(f"\n{test['desc']}: {test['amount']}₽ → ожидается {test['expected']} публикаций")
        
        # Здесь можно добавить логику проверки, но пока просто выводим
        print(f"   (Тест граничных значений - проверьте логи Railway)")

if __name__ == "__main__":
    test_commission()
    test_commission_ranges()
