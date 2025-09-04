# Файл: balance_manager.py
import asyncio
import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional
import logging

class BalanceManager:
    def __init__(self, db_path: str = "auction_bot.db"):
        self.db_path = db_path
        
    async def export_balances_to_txt(self, filename: str = "user_balances.txt") -> bool:
        """
        Экспортирует балансы всех пользователей в текстовый файл
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Получаем всех пользователей с их балансами
                cursor = await db.execute("""
                    SELECT user_id, username, full_name, balance, is_admin, created_at 
                    FROM users 
                    ORDER BY created_at DESC
                """)
                users = await cursor.fetchall()
                
                # Формируем содержимое файла
                content = []
                content.append("=" * 80)
                content.append("БАЛАНСЫ ПОЛЬЗОВАТЕЛЕЙ БОТА АУКЦИОНОВ")
                content.append("=" * 80)
                content.append(f"Дата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
                content.append(f"Всего пользователей: {len(users)}")
                content.append("=" * 80)
                content.append("")
                
                # Заголовки таблицы
                content.append(f"{'ID':<12} {'Username':<20} {'Имя':<25} {'Баланс':<10} {'Статус':<12} {'Дата регистрации'}")
                content.append("-" * 100)
                
                total_balance = 0
                admin_count = 0
                regular_users = 0
                
                for user in users:
                    user_id, username, full_name, balance, is_admin, created_at = user
                    
                    # Форматируем данные
                    username_display = f"@{username}" if username else "Нет username"
                    full_name_display = full_name or "Не указано"
                    status = "Администратор" if is_admin else "Пользователь"
                    
                    # Форматируем дату
                    if isinstance(created_at, str):
                        try:
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            date_str = date_obj.strftime('%d.%m.%Y %H:%M')
                        except ValueError:
                            date_str = created_at
                    else:
                        date_str = created_at.strftime('%d.%m.%Y %H:%M') if created_at else "Неизвестно"
                    
                    # Добавляем строку в файл
                    content.append(f"{user_id:<12} {username_display:<20} {full_name_display:<25} {balance:<10} {status:<12} {date_str}")
                    
                    # Подсчитываем статистику
                    if is_admin:
                        admin_count += 1
                    else:
                        regular_users += 1
                        total_balance += balance
                
                content.append("-" * 100)
                content.append("")
                content.append("СТАТИСТИКА:")
                content.append(f"Всего пользователей: {len(users)}")
                content.append(f"Администраторов: {admin_count}")
                content.append(f"Обычных пользователей: {regular_users}")
                content.append(f"Общий баланс (без админов): {total_balance} публикаций")
                content.append("")
                content.append("=" * 80)
                content.append("КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ БАЛАНСАМИ:")
                content.append("=" * 80)
                content.append("1. Пополнить баланс пользователя:")
                content.append("   python balance_manager.py add [user_id] [amount] [description]")
                content.append("   Пример: python balance_manager.py add 123456789 5 Бонус за активность")
                content.append("")
                content.append("2. Списть с баланса пользователя:")
                content.append("   python balance_manager.py remove [user_id] [amount] [description]")
                content.append("   Пример: python balance_manager.py remove 123456789 2 Штраф")
                content.append("")
                content.append("3. Установить точный баланс пользователя:")
                content.append("   python balance_manager.py set [user_id] [amount] [description]")
                content.append("   Пример: python balance_manager.py set 123456789 10 Установка баланса")
                content.append("")
                content.append("4. Просмотреть баланс конкретного пользователя:")
                content.append("   python balance_manager.py view [user_id]")
                content.append("   Пример: python balance_manager.py view 123456789")
                content.append("")
                content.append("5. Обновить этот файл:")
                content.append("   python balance_manager.py export")
                content.append("")
                content.append("=" * 80)
                
                # Записываем в файл
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(content))
                
                logging.info(f"Балансы экспортированы в файл {filename}")
                return True
                
        except Exception as e:
            logging.error(f"Ошибка при экспорте балансов: {e}")
            return False
    
    async def get_user_balance(self, user_id: int) -> Optional[Dict]:
        """
        Получить информацию о балансе пользователя
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT user_id, username, full_name, balance, is_admin, created_at 
                    FROM users 
                    WHERE user_id = ?
                """, (user_id,))
                user = await cursor.fetchone()
                
                if not user:
                    return None
                
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'full_name': user[2],
                    'balance': user[3],
                    'is_admin': bool(user[4]),
                    'created_at': user[5]
                }
                
        except Exception as e:
            logging.error(f"Ошибка при получении баланса пользователя {user_id}: {e}")
            return None
    
    async def add_balance(self, user_id: int, amount: int, description: str = None) -> bool:
        """
        Псевдоним для update_user_balance для обратной совместимости
        """
        return await self.update_user_balance(user_id, amount, "purchase", description)
    
    async def update_user_balance(self, user_id: int, amount: int, transaction_type: str, description: str = None) -> bool:
        """
        Обновить баланс пользователя и записать транзакцию
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, существует ли пользователь
                cursor = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                if not await cursor.fetchone():
                    # Создаем пользователя, если его нет
                    await db.execute(
                        "INSERT INTO users (user_id, username, full_name, balance, is_admin) VALUES (?, ?, ?, ?, ?)",
                        (user_id, None, None, 0, False)
                    )
                
                # Обновляем баланс
                await db.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                    (amount, user_id)
                )
                
                # Записываем транзакцию
                await db.execute(
                    "INSERT INTO transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)",
                    (user_id, amount, transaction_type, description)
                )
                
                await db.commit()
                return True
                
        except Exception as e:
            logging.error(f"Ошибка при обновлении баланса пользователя {user_id}: {e}")
            return False
    
    async def set_user_balance(self, user_id: int, new_balance: int, description: str = None) -> bool:
        """
        Установить точный баланс пользователя
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Получаем текущий баланс
                cursor = await db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
                result = await cursor.fetchone()
                
                if not result:
                    # Создаем пользователя, если его нет
                    await db.execute(
                        "INSERT INTO users (user_id, username, full_name, balance, is_admin) VALUES (?, ?, ?, ?, ?)",
                        (user_id, None, None, new_balance, False)
                    )
                    difference = new_balance
                else:
                    current_balance = result[0]
                    difference = new_balance - current_balance
                    
                    # Обновляем баланс
                    await db.execute(
                        "UPDATE users SET balance = ? WHERE user_id = ?",
                        (new_balance, user_id)
                    )
                
                # Записываем транзакцию
                await db.execute(
                    "INSERT INTO transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)",
                    (user_id, difference, "admin_set_balance", description or f"Установка баланса на {new_balance}")
                )
                
                await db.commit()
                return True
                
        except Exception as e:
            logging.error(f"Ошибка при установке баланса пользователя {user_id}: {e}")
            return False
    
    async def get_transaction_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Получить историю транзакций пользователя
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT amount, transaction_type, description, created_at 
                    FROM transactions 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                transactions = await cursor.fetchall()
                
                return [
                    {
                        'amount': t[0],
                        'transaction_type': t[1],
                        'description': t[2],
                        'created_at': t[3]
                    }
                    for t in transactions
                ]
                
        except Exception as e:
            logging.error(f"Ошибка при получении истории транзакций пользователя {user_id}: {e}")
            return []


async def main():
    """
    Основная функция для работы с балансами через командную строку
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python balance_manager.py export                    - Экспортировать балансы в txt файл")
        print("  python balance_manager.py view [user_id]           - Просмотреть баланс пользователя")
        print("  python balance_manager.py add [user_id] [amount] [description] - Пополнить баланс")
        print("  python balance_manager.py remove [user_id] [amount] [description] - Списать с баланса")
        print("  python balance_manager.py set [user_id] [amount] [description] - Установить точный баланс")
        return
    
    command = sys.argv[1]
    balance_manager = BalanceManager()
    
    if command == "export":
        success = await balance_manager.export_balances_to_txt()
        if success:
            print("✅ Балансы успешно экспортированы в файл user_balances.txt")
        else:
            print("❌ Ошибка при экспорте балансов")
    
    elif command == "view":
        if len(sys.argv) < 3:
            print("❌ Укажите ID пользователя")
            return
        
        try:
            user_id = int(sys.argv[2])
            user_info = await balance_manager.get_user_balance(user_id)
            
            if user_info:
                print(f"👤 Пользователь ID: {user_info['user_id']}")
                print(f"📝 Username: @{user_info['username']}" if user_info['username'] else "📝 Username: Не указан")
                print(f"👤 Имя: {user_info['full_name']}" if user_info['full_name'] else "👤 Имя: Не указано")
                print(f"💰 Баланс: {user_info['balance']} публикаций")
                print(f"👑 Статус: {'Администратор' if user_info['is_admin'] else 'Пользователь'}")
                print(f"📅 Дата регистрации: {user_info['created_at']}")
                
                # Показываем последние транзакции
                transactions = await balance_manager.get_transaction_history(user_id, 5)
                if transactions:
                    print("\n📊 Последние транзакции:")
                    for t in transactions:
                        amount_str = f"+{t['amount']}" if t['amount'] > 0 else str(t['amount'])
                        print(f"  {amount_str} - {t['description']} ({t['created_at']})")
            else:
                print(f"❌ Пользователь с ID {user_id} не найден")
                
        except ValueError:
            print("❌ ID пользователя должен быть числом")
    
    elif command == "add":
        if len(sys.argv) < 4:
            print("❌ Укажите ID пользователя и сумму")
            return
        
        try:
            user_id = int(sys.argv[2])
            amount = int(sys.argv[3])
            description = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else "Пополнение баланса"
            
            success = await balance_manager.update_user_balance(user_id, amount, "admin_grant", description)
            
            if success:
                user_info = await balance_manager.get_user_balance(user_id)
                print(f"✅ Баланс пользователя {user_id} пополнен на {amount} публикаций")
                print(f"💰 Новый баланс: {user_info['balance']} публикаций")
            else:
                print("❌ Ошибка при пополнении баланса")
                
        except ValueError:
            print("❌ ID пользователя и сумма должны быть числами")
    
    elif command == "remove":
        if len(sys.argv) < 4:
            print("❌ Укажите ID пользователя и сумму")
            return
        
        try:
            user_id = int(sys.argv[2])
            amount = int(sys.argv[3])
            description = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else "Списание с баланса"
            
            success = await balance_manager.update_user_balance(user_id, -amount, "admin_penalty", description)
            
            if success:
                user_info = await balance_manager.get_user_balance(user_id)
                print(f"✅ С баланса пользователя {user_id} списано {amount} публикаций")
                print(f"💰 Новый баланс: {user_info['balance']} публикаций")
            else:
                print("❌ Ошибка при списании с баланса")
                
        except ValueError:
            print("❌ ID пользователя и сумма должны быть числами")
    
    elif command == "set":
        if len(sys.argv) < 4:
            print("❌ Укажите ID пользователя и новый баланс")
            return
        
        try:
            user_id = int(sys.argv[2])
            new_balance = int(sys.argv[3])
            description = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else f"Установка баланса на {new_balance}"
            
            success = await balance_manager.set_user_balance(user_id, new_balance, description)
            
            if success:
                user_info = await balance_manager.get_user_balance(user_id)
                print(f"✅ Баланс пользователя {user_id} установлен на {new_balance} публикаций")
                print(f"💰 Текущий баланс: {user_info['balance']} публикаций")
            else:
                print("❌ Ошибка при установке баланса")
                
        except ValueError:
            print("❌ ID пользователя и баланс должны быть числами")
    
    else:
        print(f"❌ Неизвестная команда: {command}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
