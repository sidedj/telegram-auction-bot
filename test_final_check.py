#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка тарифов
"""

import requests
import json
import time
import hashlib

def test_tariff(amount, expected_publications, description):
    """Тестируем конкретный тариф"""
    print(f"\n🧪 {description}")
    print(f"   Сумма: {amount}₽")
    print(f"   Ожидается: {expected_publications} публикаций")
    print("-" * 50)
    
    url = "https://web-production-fa7dc.up.railway.app/yoomoney"
    
    test_data = {
        'notification_type': 'p2p-incoming',
        'operation_id': f'test_{amount}_{int(time.time())}',
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
    
    try:
        response = requests.post(url, data=test_data, timeout=30)
        
        print(f"   📥 Статус: {response.status_code}")
        print(f"   📥 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Webhook: OK")
            
            # Анализируем результат
            if expected_publications == 0:
                if response.text == "OK":
                    print("   ✅ ПРАВИЛЬНО: 0 публикаций зачислено")
                else:
                    print("   ❌ ОШИБКА: Должно быть 0 публикаций")
            else:
                if response.text == "OK":
                    print(f"   ✅ ПРАВИЛЬНО: {expected_publications} публикаций зачислено")
                else:
                    print(f"   ❌ ОШИБКА: Должно быть {expected_publications} публикаций")
        else:
            print("   ❌ Webhook: Ошибка")
            
        return response.status_code == 200
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_all_tariffs():
    """Тестируем все тарифы"""
    print("🚀 Финальная проверка тарифов")
    print("=" * 80)
    
    # Установленные тарифы
    tariffs = [
        (50.0, 1, "1 публикация - 50₽"),
        (200.0, 5, "5 публикаций - 200₽"),
        (350.0, 10, "10 публикаций - 350₽"),
        (600.0, 20, "20 публикаций - 600₽"),
    ]
    
    # Проблемные суммы (должны давать 0 публикаций)
    problem_amounts = [
        (25.0, 0, "25₽ - НЕ должно давать публикаций"),
        (100.0, 0, "100₽ - НЕ должно давать публикаций"),
        (300.0, 0, "300₽ - НЕ должно давать публикаций"),
        (461.43, 0, "461.43₽ - НЕ должно давать публикаций"),
        (500.0, 0, "500₽ - НЕ должно давать публикаций"),
        (1000.0, 0, "1000₽ - НЕ должно давать публикаций"),
    ]
    
    print("📋 Тестируем установленные тарифы:")
    for amount, expected, description in tariffs:
        test_tariff(amount, expected, description)
    
    print("\n📋 Тестируем проблемные суммы (должны давать 0 публикаций):")
    for amount, expected, description in problem_amounts:
        test_tariff(amount, expected, description)

if __name__ == "__main__":
    test_all_tariffs()
    
    print("\n" + "=" * 80)
    print("🎉 Финальная проверка завершена!")
    print("\n💡 Если все тесты показывают правильные результаты,")
    print("   то проблема исправлена!")
    print("   Если есть ошибки - нужно проверить логи Railway")
