# Файл: services.py
# Сервисы для управления балансами, уведомлениями и админ панелью

import asyncio
import aiosqlite
import logging
from datetime import datetime
from typing import List, Dict, Optional
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from config import ADMIN_USER_IDS, DATABASE_PATH, CHANNEL_USERNAME_LINK

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
                            created_at_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            created_at_str = created_at_dt.strftime('%d.%m.%Y %H:%M')
                        except ValueError:
                            created_at_str = created_at
                    else:
                        created_at_str = created_at.strftime('%d.%m.%Y %H:%M') if created_at else "Неизвестно"
                    
                    # Добавляем строку в таблицу
                    content.append(f"{user_id:<12} {username_display:<20} {full_name_display:<25} {balance:<10} {status:<12} {created_at_str}")
                    
                    # Подсчитываем статистику
                    if is_admin:
                        admin_count += 1
                    else:
                        regular_users += 1
                        total_balance += balance
                
                # Добавляем итоговую статистику
                content.append("-" * 100)
                content.append(f"{'ИТОГО':<12} {'':<20} {'':<25} {total_balance:<10} {'':<12} {'':<15}")
                content.append("")
                content.append("СТАТИСТИКА:")
                content.append(f"  • Всего пользователей: {len(users)}")
                content.append(f"  • Администраторов: {admin_count}")
                content.append(f"  • Обычных пользователей: {regular_users}")
                content.append(f"  • Общий баланс: {total_balance} публикаций")
                content.append(f"  • Средний баланс: {total_balance // max(regular_users, 1)} публикаций")
                content.append("=" * 80)
                
                # Записываем в файл
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(content))
                
                logging.info(f"✅ Балансы экспортированы в файл {filename}")
                return True
                
        except Exception as e:
            logging.error(f"❌ Ошибка экспорта балансов: {e}")
            return False

class NotificationManager:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.bot = Bot(token=bot_token)
    
    async def send_balance_notification(self, user_id: int, amount: float, publications: int, new_balance: int) -> bool:
        """
        Отправляет уведомление о пополнении баланса
        """
        try:
            message = f"💰 <b>Пополнение баланса!</b>\n\n"
            message += f"💳 Сумма: {amount}₽\n"
            message += f"📊 Зачислено: {publications} публикаций\n"
            message += f"💎 Новый баланс: {new_balance} публикаций\n\n"
            message += f"🎉 Теперь вы можете создавать аукционы!"
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML"
            )
            
            logging.info(f"✅ Уведомление о пополнении баланса отправлено пользователю {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка отправки уведомления о пополнении баланса пользователю {user_id}: {e}")
            return False
    
    async def send_auction_created_notification(self, user_id: int, auction_description: str, auction_id: int) -> bool:
        """
        Отправляет уведомление о создании аукциона
        """
        try:
            message = f"🚀 <b>Аукцион создан!</b>\n\n"
            message += f"📝 Описание: {auction_description[:100]}{'...' if len(auction_description) > 100 else ''}\n"
            message += f"🆔 ID аукциона: {auction_id}\n\n"
            message += f"📋 Аукцион готов к публикации в канале.\n"
            message += f"💡 Нажмите кнопку 'Опубликовать' для размещения в канале."
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML"
            )
            
            logging.info(f"✅ Уведомление о создании аукциона отправлено пользователю {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка отправки уведомления о создании аукциона пользователю {user_id}: {e}")
            return False
    
    async def send_auction_published_notification(self, user_id: int, auction_description: str, auction_id: int, channel_link: str = None) -> bool:
        """
        Отправляет уведомление о публикации аукциона
        """
        try:
            message = f"📢 <b>Аукцион опубликован!</b>\n\n"
            message += f"📝 Описание: {auction_description[:100]}{'...' if len(auction_description) > 100 else ''}\n"
            message += f"🆔 ID аукциона: {auction_id}\n\n"
            
            if channel_link:
                message += f"🔗 <a href='{channel_link}'>Посмотреть в канале</a>\n\n"
            else:
                message += f"📺 Аукцион размещен в канале\n\n"
            
            message += f"💡 Теперь пользователи могут делать ставки!"
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML"
            )
            
            logging.info(f"✅ Уведомление о публикации аукциона отправлено пользователю {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка отправки уведомления о публикации аукциона пользователю {user_id}: {e}")
            return False

class AdminPanel:
    def __init__(self):
        self.db = Database(DATABASE_PATH)
        
    async def init_db(self):
        """Инициализация базы данных"""
        await self.db.init_db()
        
    async def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Получить информацию о пользователе"""
        try:
            # Убеждаемся, что база данных инициализирована
            await self.db.init_db()
            
            user = await self.db.get_or_create_user(user_id)
            return user
        except Exception as e:
            logging.error(f"Error getting user info: {e}")
            return None
    
    async def update_user_balance(self, user_id: int, amount: int, description: str = "Административное изменение") -> bool:
        """Обновить баланс пользователя"""
        try:
            # Убеждаемся, что база данных инициализирована
            await self.db.init_db()
            
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
            await self.db.init_db()
            users = await self.db.get_all_users()
            return users[:limit]
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []
    
    async def get_auction_stats(self) -> Dict:
        """Получить статистику аукционов"""
        try:
            await self.db.init_db()
            
            total_auctions = await self.db.get_total_auctions()
            active_auctions = await self.db.get_truly_active_auctions_count()
            total_users = await self.db.get_total_users()
            
            return {
                'total_auctions': total_auctions,
                'active_auctions': active_auctions,
                'total_users': total_users
            }
        except Exception as e:
            logging.error(f"Error getting auction stats: {e}")
            return {
                'total_auctions': 0,
                'active_auctions': 0,
                'total_users': 0
            }
    
    async def grant_admin_status(self, user_id: int) -> bool:
        """Выдать права администратора"""
        try:
            await self.db.init_db()
            await self.db.grant_admin_status(user_id)
            return True
        except Exception as e:
            logging.error(f"Error granting admin status: {e}")
            return False

# Функции для обратной совместимости
def init_notifications(bot_token: str) -> NotificationManager:
    """Инициализировать менеджер уведомлений"""
    return NotificationManager(bot_token)

async def send_auction_created_notification(bot, user_id: int, auction_description: str, auction_id: int) -> bool:
    """Отправить уведомление о создании аукциона"""
    notification_manager = NotificationManager(bot.token)
    return await notification_manager.send_auction_created_notification(user_id, auction_description, auction_id)

async def send_auction_published_notification(bot, user_id: int, auction_description: str, auction_id: int, channel_link: str = None) -> bool:
    """Отправить уведомление о публикации аукциона"""
    notification_manager = NotificationManager(bot.token)
    return await notification_manager.send_auction_published_notification(user_id, auction_description, auction_id, channel_link)
