#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест правильных тарифов
"""

import requests
import json
import time

def test_correct_tariffs():
    """Тестируем правильные тарифы"""
    print("🧪 Тест правильных тарифов")
    print("=" * 50)
    
    # URL основного endpoint
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    # Тестовые случаи с правильными тарифами
    test_cases = [
        {
            'amount': '50.00',
            'expected_publications': 1,
            'description': '50₽ = 1 публикация'
        },
        {
            'amount': '200.00',
            'expected_publications': 5,
            'description': '200₽ = 5 публикаций'
        },
        {
            'amount': '350.00',
            'expected_publications': 10,
            'description': '350₽ = 10 публикаций'
        },
        {
            'amount': '600.00',
            'expected_publications': 20,
            'description': '600₽ = 20 публикаций'
        },
        {
            'amount': '25.00',
            'expected_publications': 0,
            'description': '25₽ = 0 публикаций (слишком мало)'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Ожидается: {case['expected_publications']} публикаций")
        
        # Данные платежа
        payment_data = {
            'notification_type': 'card-incoming',
            'operation_id': f'test_tariff_{i}',
            'amount': case['amount'],
            'withdraw_amount': case['amount'],
            'currency': '643',
            'datetime': '2025-09-06T19:00:00.000Z',
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

def test_commission_tariffs():
    """Тестируем тарифы с комиссией"""
    print("\n🔍 Тест тарифов с комиссией")
    print("=" * 50)
    
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    # Тесты с комиссией
    commission_tests = [
        {
            'amount': '54.00',  # 50₽ + 4₽ комиссия
            'withdraw_amount': '50.00',
            'expected_publications': 1,
            'description': '50₽ + 4₽ комиссия = 1 публикация'
        },
        {
            'amount': '216.00',  # 200₽ + 16₽ комиссия
            'withdraw_amount': '200.00',
            'expected_publications': 5,
            'description': '200₽ + 16₽ комиссия = 5 публикаций'
        },
        {
            'amount': '378.00',  # 350₽ + 28₽ комиссия
            'withdraw_amount': '350.00',
            'expected_publications': 10,
            'description': '350₽ + 28₽ комиссия = 10 публикаций'
        }
    ]
    
    for i, test in enumerate(commission_tests, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Сумма: {test['amount']}₽ → {test['withdraw_amount']}₽")
        print(f"   Ожидается: {test['expected_publications']} публикаций")
        
        # Данные платежа
        payment_data = {
            'notification_type': 'card-incoming',
            'operation_id': f'test_commission_{i}',
            'amount': test['amount'],
            'withdraw_amount': test['withdraw_amount'],
            'currency': '643',
            'datetime': '2025-09-06T19:00:00.000Z',
            'sender': '41001000040',
            'codepro': 'false',
            'label': 'user_476589798'
        }
        
        try:
            # Отправляем запрос
            response = requests.post(url, data=payment_data, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Webhook: OK")
            else:
                print(f"   ❌ Webhook: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Небольшая пауза между запросами
        time.sleep(1)

if __name__ == "__main__":
    test_correct_tariffs()
    test_commission_tariffs()
