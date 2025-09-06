#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест накопления баланса при нескольких пополнениях
"""

import requests
import json
import time
import hashlib

def test_balance_accumulation():
    """Тестируем накопление баланса при нескольких пополнениях"""
    print("🧪 Тест накопления баланса")
    print("=" * 60)
    
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    user_id = 476589798  # Тестовый пользователь
    
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
            'operation_id': f'balance_test_{i}_{int(time.time())}',
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
        
        # Небольшая пауза между платежами
        time.sleep(1)
    
    print(f"\n🎯 Итоговый ожидаемый баланс: {total_expected} публикаций")
    print("💡 Проверьте в боте, что баланс накопился правильно")

def test_balance_display():
    """Тестируем отображение баланса в разных местах"""
    print("\n🔍 Тест отображения баланса")
    print("=" * 60)
    
    print("📋 Места где должен отображаться баланс:")
    print("   1. Главное меню - кнопка 'Пополнить баланс 💳 (X)'")
    print("   2. Приветственное сообщение - 'Ваш баланс: X публикаций'")
    print("   3. Статистика - 'Баланс: X публикаций'")
    print("   4. Статус платежей - 'Ваш баланс: X публикаций'")
    print("   5. При пополнении - 'Ваш текущий баланс: X публикаций'")
    print("   6. При создании аукциона - проверка баланса")
    
    print("\n💡 Проверьте в боте, что баланс отображается везде одинаково")

def test_balance_persistence():
    """Тестируем сохранение баланса"""
    print("\n🔍 Тест сохранения баланса")
    print("=" * 60)
    
    print("📋 Что должно происходить:")
    print("   1. При пополнении баланс должен УВЕЛИЧИВАТЬСЯ (не заменяться)")
    print("   2. Баланс должен сохраняться между сессиями")
    print("   3. При перезапуске бота баланс не должен сбрасываться")
    print("   4. Транзакции должны записываться в базу данных")
    
    print("\n💡 Проверьте в боте, что баланс сохраняется правильно")

if __name__ == "__main__":
    print("🚀 Тест системы баланса")
    print("=" * 80)
    
    test_balance_accumulation()
    test_balance_display()
    test_balance_persistence()
    
    print("\n" + "=" * 80)
    print("🎉 Тестирование системы баланса завершено!")
    print("\n💡 Рекомендации:")
    print("   1. Проверьте в боте, что баланс накапливается при нескольких пополнениях")
    print("   2. Убедитесь, что баланс отображается везде одинаково")
    print("   3. Проверьте, что баланс сохраняется между сессиями")
