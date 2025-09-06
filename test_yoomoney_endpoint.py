#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест основного endpoint /yoomoney
"""

import requests
import json
import time

def test_yoomoney_endpoint():
    """Тестируем основной endpoint /yoomoney"""
    print("🚀 Тест основного endpoint /yoomoney")
    print("=" * 50)
    
    # URL основного endpoint
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    # Тестовые данные реального платежа
    payment_data = {
        'notification_type': 'card-incoming',
        'operation_id': 'real_payment_yoomoney_123',
        'amount': '200.00',
        'withdraw_amount': '200.00',
        'currency': '643',
        'datetime': '2025-09-06T18:30:00.000Z',
        'sender': '41001000040',
        'codepro': 'false',
        'label': 'user_476589798'
    }
    
    print("🧪 Тестируем реальный платеж 200₽ на /yoomoney...")
    print("📤 Отправляем данные:")
    for key, value in payment_data.items():
        print(f"   {key}: {value}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(url, data=payment_data, timeout=10)
        
        print(f"\n📥 Ответ сервера:")
        print(f"   Статус: {response.status_code}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook работает!")
            
            # Ждем обработки
            print("\n⏳ Ждем обработки данных...")
            time.sleep(3)
            
            print("💡 Проверьте логи Railway - там должны быть записи:")
            print("   - '=== YOOMONEY WEBHOOK VERSION 15.0 - ОСНОВНОЙ ENDPOINT ==='")
            print("   - '🔧 Обрабатываем платеж - начисляем баланс'")
            print("   - '✅ Начислено 4 публикаций пользователю 476589798 за 200.0₽'")
            print("   - '✅ Уведомление отправлено пользователю 476589798'")
            
            return True
        else:
            print("❌ Webhook не работает!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_different_amounts_yoomoney():
    """Тестируем разные суммы на /yoomoney"""
    print("\n🧪 Тестируем разные суммы на /yoomoney")
    print("=" * 50)
    
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    test_cases = [
        {'amount': '50.00', 'expected': 1, 'description': '50₽ = 1 публикация'},
        {'amount': '200.00', 'expected': 4, 'description': '200₽ = 4 публикации'},
        {'amount': '350.00', 'expected': 7, 'description': '350₽ = 7 публикаций'},
        {'amount': '25.00', 'expected': 0, 'description': '25₽ = 0 публикаций (слишком мало)'}
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        
        data = {
            'notification_type': 'card-incoming',
            'operation_id': f'test_yoomoney_{i}',
            'amount': case['amount'],
            'withdraw_amount': case['amount'],
            'currency': '643',
            'datetime': '2025-09-06T18:30:00.000Z',
            'sender': '41001000040',
            'codepro': 'false',
            'label': 'user_476589798'
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            print(f"   Статус: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   Ошибка: {e}")

if __name__ == "__main__":
    test_yoomoney_endpoint()
    test_different_amounts_yoomoney()
