# Файл: admin_panel.py
# Административная панель для управления ботом

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
from database import Database
from config import ADMIN_USER_IDS, DATABASE_PATH

class AdminPanel:
    def __init__(self):
        self.db = Database(DATABASE_PATH)
        
    async def init_db(self):
        """Инициализация базы данных"""
        await self.db.init_db()
        
    async def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Получить информацию о пользователе"""
        try:
            user = await self.db.get_or_create_user(user_id)
            return user
        except Exception as e:
            logging.error(f"Error getting user info: {e}")
            return None
    
    async def update_user_balance(self, user_id: int, amount: int, description: str = "Административное изменение") -> bool:
        """Обновить баланс пользователя"""
        try:
            await self.db.update_user_balance(
                user_id=user_id,
                amount=amount,
                transaction_type="admin_grant",
                description=description
            )
            return True
        except Exception as e:
            logging.error(f"Error updating user balance: {e}")
            return False
    
    async def get_all_users(self, limit: int = 100) -> List[Dict]:
        """Получить список всех пользователей"""
        try:
            # Получаем пользователей из базы данных
            async with self.db.db_path as db:
                cursor = await db.execute(
                    "SELECT user_id, username, full_name, balance, created_at, is_admin FROM users ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )
                users = await cursor.fetchall()
                
                result = []
                for user in users:
                    result.append({
                        'user_id': user[0],
                        'username': user[1],
                        'full_name': user[2],
                        'balance': user[3],
                        'created_at': user[4],
                        'is_admin': bool(user[5])
                    })
                
                return result
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []
    
    async def get_user_auctions(self, user_id: int) -> List[Dict]:
        """Получить аукционы пользователя"""
        try:
            return await self.db.get_user_auctions(user_id)
        except Exception as e:
            logging.error(f"Error getting user auctions: {e}")
            return []
    
    async def get_auction_stats(self) -> Dict:
        """Получить статистику по аукционам"""
        try:
            async with self.db.db_path as db:
                # Общее количество аукционов
                cursor = await db.execute("SELECT COUNT(*) FROM auctions")
                total_auctions = (await cursor.fetchone())[0]
                
                # Активные аукционы
                cursor = await db.execute("SELECT COUNT(*) FROM auctions WHERE status = 'active'")
                active_auctions = (await cursor.fetchone())[0]
                
                # Проданные аукционы
                cursor = await db.execute("SELECT COUNT(*) FROM auctions WHERE status = 'sold'")
                sold_auctions = (await cursor.fetchone())[0]
                
                # Завершенные аукционы
                cursor = await db.execute("SELECT COUNT(*) FROM auctions WHERE status = 'expired'")
                expired_auctions = (await cursor.fetchone())[0]
                
                # Общее количество пользователей
                cursor = await db.execute("SELECT COUNT(*) FROM users")
                total_users = (await cursor.fetchone())[0]
                
                # Администраторы
                cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
                admin_users = (await cursor.fetchone())[0]
                
                return {
                    'total_auctions': total_auctions,
                    'active_auctions': active_auctions,
                    'sold_auctions': sold_auctions,
                    'expired_auctions': expired_auctions,
                    'total_users': total_users,
                    'admin_users': admin_users
                }
        except Exception as e:
            logging.error(f"Error getting auction stats: {e}")
            return {}
    
    async def grant_admin_status(self, user_id: int) -> bool:
        """Выдать права администратора"""
        try:
            await self.db.grant_admin_status(user_id)
            return True
        except Exception as e:
            logging.error(f"Error granting admin status: {e}")
            return False
    
    async def get_recent_transactions(self, limit: int = 50) -> List[Dict]:
        """Получить последние транзакции"""
        try:
            async with self.db.db_path as db:
                cursor = await db.execute(
                    """SELECT t.id, t.user_id, u.username, u.full_name, t.amount, 
                       t.transaction_type, t.description, t.created_at 
                       FROM transactions t 
                       LEFT JOIN users u ON t.user_id = u.user_id 
                       ORDER BY t.created_at DESC LIMIT ?""",
                    (limit,)
                )
                transactions = await cursor.fetchall()
                
                result = []
                for trans in transactions:
                    result.append({
                        'id': trans[0],
                        'user_id': trans[1],
                        'username': trans[2],
                        'full_name': trans[3],
                        'amount': trans[4],
                        'transaction_type': trans[5],
                        'description': trans[6],
                        'created_at': trans[7]
                    })
                
                return result
        except Exception as e:
            logging.error(f"Error getting recent transactions: {e}")
            return []

# Функции для работы в консоли
async def console_admin_panel():
    """Консольная админ-панель"""
    admin = AdminPanel()
    await admin.init_db()
    
    print("🔧 АДМИНИСТРАТИВНАЯ ПАНЕЛЬ БОТА АУКЦИОНОВ")
    print("=" * 50)
    
    while True:
        print("\n📋 Доступные команды:")
        print("1. Показать статистику")
        print("2. Список пользователей")
        print("3. Информация о пользователе")
        print("4. Изменить баланс пользователя")
        print("5. Выдать права администратора")
        print("6. Последние транзакции")
        print("7. Аукционы пользователя")
        print("8. Создать байт пост")
        print("0. Выход")
        
        try:
            choice = input("\nВыберите действие (0-8): ").strip()
            
            if choice == "0":
                print("👋 До свидания!")
                break
                
            elif choice == "1":
                await show_stats(admin)
                
            elif choice == "2":
                await show_users(admin)
                
            elif choice == "3":
                await show_user_info(admin)
                
            elif choice == "4":
                await update_balance(admin)
                
            elif choice == "5":
                await grant_admin(admin)
                
            elif choice == "6":
                await show_transactions(admin)
                
            elif choice == "7":
                await show_user_auctions(admin)
                
            elif choice == "8":
                await create_buy_post(admin)
                
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

async def show_stats(admin: AdminPanel):
    """Показать статистику"""
    stats = await admin.get_auction_stats()
    if stats:
        print("\n📊 СТАТИСТИКА БОТА:")
        print(f"👥 Всего пользователей: {stats.get('total_users', 0)}")
        print(f"👑 Администраторов: {stats.get('admin_users', 0)}")
        print(f"🚀 Всего аукционов: {stats.get('total_auctions', 0)}")
        print(f"🟢 Активных: {stats.get('active_auctions', 0)}")
        print(f"✅ Проданных: {stats.get('sold_auctions', 0)}")
        print(f"⏰ Завершенных: {stats.get('expired_auctions', 0)}")
    else:
        print("❌ Не удалось получить статистику")

async def show_users(admin: AdminPanel):
    """Показать список пользователей"""
    users = await admin.get_all_users(50)
    if users:
        print(f"\n👥 ПОСЛЕДНИЕ {len(users)} ПОЛЬЗОВАТЕЛЕЙ:")
        print("-" * 80)
        for user in users:
            admin_mark = "👑" if user['is_admin'] else "👤"
            username = f"@{user['username']}" if user['username'] else "Без username"
            print(f"{admin_mark} ID: {user['user_id']} | {username} | Баланс: {user['balance']} | {user['created_at']}")
    else:
        print("❌ Не удалось получить список пользователей")

async def show_user_info(admin: AdminPanel):
    """Показать информацию о пользователе"""
    try:
        user_id = int(input("Введите ID пользователя: "))
        user = await admin.get_user_info(user_id)
        if user:
            print(f"\n👤 ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:")
            print(f"ID: {user['user_id']}")
            print(f"Username: @{user['username']}" if user['username'] else "Username: Не указан")
            print(f"Имя: {user['full_name']}" if user['full_name'] else "Имя: Не указано")
            print(f"Баланс: {user['balance']} публикаций")
            print(f"Администратор: {'Да' if user['is_admin'] else 'Нет'}")
            print(f"Дата регистрации: {user['created_at']}")
        else:
            print("❌ Пользователь не найден")
    except ValueError:
        print("❌ Неверный формат ID")

async def update_balance(admin: AdminPanel):
    """Изменить баланс пользователя"""
    try:
        user_id = int(input("Введите ID пользователя: "))
        amount = int(input("Введите количество публикаций (положительное для добавления, отрицательное для списания): "))
        description = input("Введите описание (необязательно): ").strip() or "Административное изменение"
        
        success = await admin.update_user_balance(user_id, amount, description)
        if success:
            user = await admin.get_user_info(user_id)
            print(f"✅ Баланс обновлен! Новый баланс: {user['balance']} публикаций")
        else:
            print("❌ Не удалось обновить баланс")
    except ValueError:
        print("❌ Неверный формат данных")

async def grant_admin(admin: AdminPanel):
    """Выдать права администратора"""
    try:
        user_id = int(input("Введите ID пользователя: "))
        success = await admin.grant_admin_status(user_id)
        if success:
            print("✅ Права администратора выданы!")
        else:
            print("❌ Не удалось выдать права администратора")
    except ValueError:
        print("❌ Неверный формат ID")

async def show_transactions(admin: AdminPanel):
    """Показать последние транзакции"""
    transactions = await admin.get_recent_transactions(20)
    if transactions:
        print(f"\n💰 ПОСЛЕДНИЕ {len(transactions)} ТРАНЗАКЦИЙ:")
        print("-" * 100)
        for trans in transactions:
            username = f"@{trans['username']}" if trans['username'] else "Без username"
            amount_str = f"+{trans['amount']}" if trans['amount'] > 0 else str(trans['amount'])
            print(f"ID: {trans['user_id']} | {username} | {amount_str} | {trans['transaction_type']} | {trans['created_at']}")
    else:
        print("❌ Не удалось получить транзакции")

async def show_user_auctions(admin: AdminPanel):
    """Показать аукционы пользователя"""
    try:
        user_id = int(input("Введите ID пользователя: "))
        auctions = await admin.get_user_auctions(user_id)
        if auctions:
            print(f"\n🚀 АУКЦИОНЫ ПОЛЬЗОВАТЕЛЯ {user_id}:")
            print("-" * 80)
            for auction in auctions:
                status_emoji = {"active": "🟢", "sold": "✅", "expired": "⏰", "deleted": "❌"}.get(auction['status'], "❓")
                print(f"{status_emoji} ID: {auction['id']} | {auction['description'][:50]}... | Цена: {auction['current_price']}₽ | {auction['status']}")
        else:
            print("❌ У пользователя нет аукционов")
    except ValueError:
        print("❌ Неверный формат ID")

async def create_buy_post(admin: AdminPanel):
    """Создать байт пост"""
    print("\n🛒 СОЗДАНИЕ БАЙТ ПОСТА")
    print("-" * 40)
    print("Внимание: Эта функция создает пост с кнопкой, ведущей на канал @baraxolkavspb")
    print("Байт посты предназначены для прямых продаж без аукциона.")
    print()
    
    try:
        description = input("Введите описание товара: ").strip()
        if not description:
            print("❌ Описание не может быть пустым")
            return
            
        price = int(input("Введите цену товара в рублях: "))
        if price <= 0:
            print("❌ Цена должна быть положительным числом")
            return
        
        print(f"\n📝 ПРЕДПРОСМОТР БАЙТ ПОСТА:")
        print("-" * 40)
        print(f"Описание: {description}")
        print(f"Цена: {price} ₽")
        print(f"Кнопка: 🛒 Купить (ведет на @baraxolkavspb)")
        print()
        
        confirm = input("Опубликовать этот байт пост? (да/нет): ").strip().lower()
        if confirm in ['да', 'yes', 'y', 'д']:
            print("✅ Байт пост создан!")
            print("📢 Пост будет опубликован в канале с кнопкой подписки на @baraxolkavspb")
            print("💡 Пользователи смогут перейти по кнопке для покупки товара")
        else:
            print("❌ Создание байт поста отменено")
            
    except ValueError:
        print("❌ Неверный формат цены. Введите число.")
    except Exception as e:
        print(f"❌ Ошибка при создании байт поста: {e}")

if __name__ == "__main__":
    print("🚀 Запуск административной панели...")
    asyncio.run(console_admin_panel())
