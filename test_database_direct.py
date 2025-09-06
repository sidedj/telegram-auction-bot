#!/usr/bin/env python3
"""
Прямой тест базы данных
"""
import asyncio
import logging
from database import Database

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_database_operations():
    """Тестирует операции с базой данных"""
    print("🗄️ Тестируем операции с базой данных...")
    
    # Создаем экземпляр базы данных
    db = Database()
    
    # Инициализируем базу данных
    await db.init_db()
    print("✅ База данных инициализирована")
    
    # Тестовый user_id
    test_user_id = 476589798
    
    try:
        # Тест 1: Получаем текущий баланс
        print(f"\n1️⃣ Получаем текущий баланс пользователя {test_user_id}...")
        current_balance = await db.get_user_balance(test_user_id)
        print(f"   Текущий баланс: {current_balance}")
        
        # Тест 2: Обновляем баланс
        print(f"\n2️⃣ Обновляем баланс (+5 публикаций)...")
        success = await db.update_user_balance(
            user_id=test_user_id,
            amount=5,
            transaction_type="test_payment",
            description="Тестовое пополнение"
        )
        print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
        
        # Тест 3: Проверяем новый баланс
        print(f"\n3️⃣ Проверяем новый баланс...")
        new_balance = await db.get_user_balance(test_user_id)
        print(f"   Новый баланс: {new_balance}")
        
        # Тест 4: Получаем информацию о пользователе
        print(f"\n4️⃣ Получаем информацию о пользователе...")
        user_info = await db.get_or_create_user(test_user_id)
        print(f"   Информация о пользователе: {user_info}")
        
        # Тест 5: Получаем историю транзакций
        print(f"\n5️⃣ Получаем историю транзакций...")
        transactions = await db.get_user_transactions(test_user_id, limit=5)
        print(f"   Количество транзакций: {len(transactions)}")
        for i, transaction in enumerate(transactions, 1):
            print(f"   {i}. {transaction['amount']} - {transaction['description']} ({transaction['created_at']})")
        
        print(f"\n🎉 Все тесты базы данных прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании базы данных: {e}")
        return False

async def test_balance_operations():
    """Тестирует операции с балансом"""
    print("\n💰 Тестируем операции с балансом...")
    
    db = Database()
    await db.init_db()
    
    test_user_id = 476589798
    
    try:
        # Получаем начальный баланс
        initial_balance = await db.get_user_balance(test_user_id)
        print(f"Начальный баланс: {initial_balance}")
        
        # Добавляем 10 публикаций
        print("Добавляем 10 публикаций...")
        success = await db.update_user_balance(
            user_id=test_user_id,
            amount=10,
            transaction_type="test_add",
            description="Тестовое добавление 10 публикаций"
        )
        
        if success:
            new_balance = await db.get_user_balance(test_user_id)
            print(f"Новый баланс: {new_balance}")
            print(f"Ожидаемый баланс: {initial_balance + 10}")
            
            if new_balance == initial_balance + 10:
                print("✅ Баланс обновлен корректно!")
                return True
            else:
                print("❌ Баланс обновлен некорректно!")
                return False
        else:
            print("❌ Ошибка обновления баланса!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании баланса: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тестирование базы данных")
    print("=" * 50)
    
    # Запускаем тесты
    async def run_tests():
        test1 = await test_database_operations()
        test2 = await test_balance_operations()
        
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print("=" * 50)
        print(f"Операции с БД: {'✅ Успешно' if test1 else '❌ Ошибка'}")
        print(f"Операции с балансом: {'✅ Успешно' if test2 else '❌ Ошибка'}")
        
        if test1 and test2:
            print("\n🎉 Все тесты прошли успешно!")
        else:
            print("\n⚠️ Некоторые тесты не прошли")
        
        print("\n✨ Тестирование завершено!")
    
    asyncio.run(run_tests())
