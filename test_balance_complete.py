#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный тест системы баланса
"""

import requests
import json
import time
import hashlib

def test_complete_balance_system():
    """Полный тест системы баланса"""
    print("🚀 Полный тест системы баланса")
    print("=" * 80)
    
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    user_id = 476589798  # Тестовый пользователь
    
    print("📋 Тестируем полный цикл накопления баланса:")
    print("   1. Первое пополнение: 50₽ = 1 публикация")
    print("   2. Второе пополнение: 200₽ = 5 публикаций") 
    print("   3. Третье пополнение: 350₽ = 10 публикаций")
    print("   4. Итого должно быть: 16 публикаций")
    
    # Тестовые пополнения
    payments = [
        {'amount': 50.0, 'expected_publications': 1, 'description': 'Первое пополнение: 50₽ = 1 публикация'},
        {'amount': 200.0, 'expected_publications': 5, 'description': 'Второе пополнение: 200₽ = 5 публикаций'},
        {'amount': 350.0, 'expected_publications': 10, 'description': 'Третье пополнение: 350₽ = 10 публикаций'},
    ]
    
    total_expected = 0
    
    for i, payment in enumerate(payments, 1):
        print(f"\n{i}. {payment['description']}")
        print(f"   Ожидается: +{payment['expected_publications']} публикаций")
        total_expected += payment['expected_publications']
        print(f"   Общий ожидаемый баланс: {total_expected} публикаций")
        
        test_data = {
            'notification_type': 'p2p-incoming',
            'operation_id': f'complete_test_{i}_{int(time.time())}',
            'amount': str(payment['amount']),
            'withdraw_amount': str(payment['amount']),
            'currency': '643',
            'datetime': '2024-01-01T12:00:00.000Z',
            'sender': '41001000040',
            'codepro': 'false',
            'label': f'user_{user_id}',
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
        
        # Пауза между платежами
        time.sleep(2)
    
    print(f"\n🎯 Итоговый ожидаемый баланс: {total_expected} публикаций")
    
    print("\n" + "=" * 80)
    print("✅ ТЕСТ ЗАВЕРШЕН!")
    print("\n💡 Что проверить в боте:")
    print("   1. Главное меню должно показывать актуальный баланс")
    print("   2. При нажатии 'Пополнить баланс' должен показываться правильный баланс")
    print("   3. В статистике должен отображаться правильный баланс")
    print("   4. При создании аукциона должен проверяться правильный баланс")
    print("   5. Уведомления о пополнении должны показывать правильный баланс")
    
    print(f"\n🎉 Если все работает правильно, то баланс должен накапливаться")
    print(f"   и отображаться везде одинаково: {total_expected} публикаций")

if __name__ == "__main__":
    test_complete_balance_system()
