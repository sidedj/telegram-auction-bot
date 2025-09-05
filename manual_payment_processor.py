#!/usr/bin/env python3
"""
Ручной обработчик платежей для срочного решения проблемы
"""

import sqlite3
import requests
import time
from datetime import datetime

def get_user_balance(user_id: int) -> int:
    """Получает баланс пользователя"""
    try:
        with sqlite3.connect("auction_bot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        print(f"Ошибка при получении баланса: {e}")
        return 0

def update_user_balance(user_id: int, new_balance: int):
    """Обновляет баланс пользователя"""
    try:
        with sqlite3.connect("auction_bot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            else:
                cursor.execute("INSERT INTO users (user_id, balance, created_at) VALUES (?, ?, datetime('now'))", (user_id, new_balance))
            conn.commit()
            print(f"✅ Баланс пользователя {user_id} обновлен: {new_balance}")
    except Exception as e:
        print(f"❌ Ошибка при обновлении баланса: {e}")

def send_telegram_message(user_id: int, message: str):
    """Отправляет сообщение пользователю в Telegram"""
    try:
        bot_token = "8486386170:AAEGHCYOtGlx3TrmZ3e9vQ7p8PbtCgs0YMw"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': user_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Сообщение отправлено пользователю {user_id}")
            return True
        else:
            print(f"❌ Ошибка отправки сообщения: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка отправки Telegram сообщения: {e}")
        return False

def process_payment_manually(user_id: int, amount: float, description: str = ""):
    """Обрабатывает платеж вручную"""
    print(f"\n=== Обработка платежа ===")
    print(f"Пользователь: {user_id}")
    print(f"Сумма: {amount} ₽")
    print(f"Описание: {description}")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Определяем количество публикаций по сумме (учитывая комиссию ЮMoney)
    if amount >= 48.0 and amount <= 52.0:  # 50₽ с комиссией (48.50₽)
        publications = 1
        expected_amount = 50
    elif amount >= 195.0 and amount <= 205.0:  # 200₽ с комиссией (~198₽)
        publications = 5
        expected_amount = 200
    elif amount >= 340.0 and amount <= 360.0:  # 350₽ с комиссией (~348₽)
        publications = 10
        expected_amount = 350
    elif amount >= 590.0 and amount <= 610.0:  # 600₽ с комиссией (~598₽)
        publications = 20
        expected_amount = 600
    else:
        print(f"❌ Неизвестная сумма: {amount} ₽")
        print("Доступные суммы: 48-52₽ (1 публикация), 195-205₽ (5 публикаций), 340-360₽ (10 публикаций), 590-610₽ (20 публикаций)")
        return False
    
    # Получаем текущий баланс
    current_balance = get_user_balance(user_id)
    new_balance = current_balance + publications
    
    # Обновляем баланс
    update_user_balance(user_id, new_balance)
    
    # Отправляем уведомление (показываем номинальную сумму, а не с комиссией)
    message = f"💰 <b>Платеж получен!</b>\n\n"
    message += f"Сумма: {expected_amount} ₽\n"
    message += f"Начислено: {publications} публикаций\n"
    message += f"Ваш баланс: {new_balance} публикаций\n\n"
    message += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    success = send_telegram_message(user_id, message)
    
    if success:
        print(f"✅ Пользователю {user_id} начислено {publications} публикаций")
        print(f"✅ Новый баланс: {new_balance} публикаций")
        return True
    else:
        print(f"❌ Ошибка отправки уведомления")
        return False

def main():
    print("=== РУЧНОЙ ОБРАБОТЧИК ПЛАТЕЖЕЙ ===")
    print("Используйте этот скрипт для срочной обработки платежей")
    print("когда автоматические уведомления не работают")
    
    # Ваш ID пользователя
    user_id = 7647551803
    
    print(f"\nТекущий баланс: {get_user_balance(user_id)} публикаций")
    
    while True:
        print("\n" + "="*50)
        print("Выберите действие:")
        print("1. Обработать платеж 50₽ (1 публикация)")
        print("2. Обработать платеж 200₽ (5 публикаций)")
        print("3. Обработать платеж 350₽ (10 публикаций)")
        print("4. Обработать платеж 600₽ (20 публикаций)")
        print("5. Обработать произвольную сумму")
        print("6. Показать баланс")
        print("0. Выход")
        
        choice = input("\nВведите номер: ").strip()
        
        if choice == "1":
            process_payment_manually(user_id, 50, "1 публикация")
        elif choice == "2":
            process_payment_manually(user_id, 200, "5 публикаций")
        elif choice == "3":
            process_payment_manually(user_id, 350, "10 публикаций")
        elif choice == "4":
            process_payment_manually(user_id, 600, "20 публикаций")
        elif choice == "5":
            try:
                amount = float(input("Введите сумму платежа: "))
                process_payment_manually(user_id, amount, "Произвольная сумма")
            except ValueError:
                print("❌ Неверная сумма")
        elif choice == "6":
            balance = get_user_balance(user_id)
            print(f"Текущий баланс: {balance} публикаций")
        elif choice == "0":
            break
        else:
            print("❌ Неверный выбор")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
