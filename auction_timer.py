# Файл: auction_timer.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from database import Database
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_USERNAME_LINK

class AuctionTimer:
    def __init__(self, bot: Bot, db: Database, channel_username: str):
        self.bot = bot
        self.db = db
        self.channel_username = channel_username
        self.running = False
        self.task = None

    async def check_user_subscription(self, user_id: int) -> bool:
        """Проверяет, подписан ли пользователь на канал"""
        try:
            # Получаем информацию о статусе подписки пользователя
            chat_member = await self.bot.get_chat_member(chat_id=self.channel_username, user_id=user_id)
            
            # Проверяем статус подписки
            # member, administrator, creator - активные подписчики
            # left, kicked - не подписан
            return chat_member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            logging.error(f"Error checking subscription for user {user_id}: {e}")
            # В случае ошибки считаем, что пользователь не подписан
            return False

    async def start(self):
        """Запустить таймер проверки аукционов"""
        if self.running:
            return
            
        self.running = True
        self.task = asyncio.create_task(self._check_auctions_loop())
        logging.info("Auction timer started")

    async def stop(self):
        """Остановить таймер"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logging.info("Auction timer stopped")

    async def _check_auctions_loop(self):
        """Основной цикл проверки аукционов"""
        while self.running:
            try:
                await self._check_expired_auctions()
                await asyncio.sleep(30)  # Проверяем каждые 30 секунд
            except Exception as e:
                logging.error(f"Error in auction timer loop: {e}")
                await asyncio.sleep(60)  # При ошибке ждем минуту

    async def _check_expired_auctions(self):
        """Проверить истекшие аукционы"""
        try:
            expired_auctions = await self.db.get_expired_auctions()
            
            for auction in expired_auctions:
                await self._finalize_auction(auction)
                
        except Exception as e:
            logging.error(f"Error checking expired auctions: {e}")

    async def _finalize_auction(self, auction: Dict):
        """Завершить аукцион"""
        try:
            auction_id = auction['id']
            owner_id = auction['owner_id']
            current_leader_id = auction['current_leader_id']
            current_leader_username = auction['current_leader_username']
            current_price = auction['current_price']
            description = auction['description']
            channel_chat_id = auction['channel_chat_id']
            channel_message_id = auction['channel_message_id']
            
            # Обновляем статус аукциона
            await self.db.update_auction_status(auction_id, 'expired')
            
            # Определяем результат аукциона
            if current_leader_id and current_price > auction['start_price']:
                # Аукцион завершен с победителем
                status_text = f"🏆 <b>АУКЦИОН ЗАВЕРШЕН</b>\n\n"
                status_text += f"<b>Победитель:</b> @{current_leader_username}\n"
                status_text += f"<b>Финальная цена:</b> {current_price} ₽\n\n"
                status_text += "Поздравляем с победой! Свяжитесь с продавцом для завершения сделки."
                
                # Уведомляем победителя
                try:
                    # Проверяем подписку победителя перед созданием ссылки на пост
                    winner_subscribed = await self.check_user_subscription(current_leader_id)
                    
                    keyboard_buttons = []
                    if winner_subscribed and channel_message_id:
                        # Создаем ссылку на пост аукциона только если пользователь подписан
                        # Используем username канала для ссылок
                        auction_link = f"https://t.me/{CHANNEL_USERNAME_LINK}/{channel_message_id}"
                        
                        keyboard_buttons.append([InlineKeyboardButton(text="🔗 Перейти к посту", url=auction_link)])
                    elif not winner_subscribed:
                        # Если пользователь не подписан, предлагаем подписаться
                        keyboard_buttons.append([InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{self.channel_username.replace('@', '')}")])
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons) if keyboard_buttons else None
                    
                    await self.bot.send_message(
                        chat_id=current_leader_id,
                        text=f"🎉 <b>Поздравляем!</b>\n\n"
                             f"Вы выиграли аукцион: <b>{description}</b>\n"
                             f"Ваша ставка: <b>{current_price} ₽</b>\n\n"
                             f"Свяжитесь с продавцом для завершения сделки.",
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logging.warning(f"Failed to notify winner {current_leader_id}: {e}")
                
                # Уведомляем продавца с кнопкой истории ставок
                try:
                    # Проверяем подписку продавца перед созданием ссылки на пост
                    seller_subscribed = await self.check_user_subscription(owner_id)
                    
                    # Создаем клавиатуру с кнопкой истории ставок
                    keyboard_buttons = [
                        [InlineKeyboardButton(text="📊 История ставок", callback_data=f"history_{auction_id}")]
                    ]
                    
                    # Добавляем кнопку ссылки на пост только если продавец подписан
                    if seller_subscribed and channel_message_id:
                        # Используем username канала для ссылок
                        auction_link = f"https://t.me/{CHANNEL_USERNAME_LINK}/{channel_message_id}"
                        
                        keyboard_buttons.append([InlineKeyboardButton(text="🔗 Перейти к посту", url=auction_link)])
                    elif not seller_subscribed:
                        # Если продавец не подписан, предлагаем подписаться
                        keyboard_buttons.append([InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{self.channel_username.replace('@', '')}")])
                    
                    history_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
                    
                    await self.bot.send_message(
                        chat_id=owner_id,
                        text=f"✅ <b>Аукцион завершен</b>\n\n"
                             f"Ваш лот <b>{description}</b> продан за <b>{current_price} ₽</b>\n"
                             f"Покупатель: @{current_leader_username}\n\n"
                             f"Свяжитесь с покупателем для завершения сделки.",
                        reply_markup=history_keyboard,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logging.warning(f"Failed to notify owner {owner_id}: {e}")
                    
            else:
                # Аукцион завершен без ставок
                status_text = f"⏰ <b>АУКЦИОН ЗАВЕРШЕН</b>\n\n"
                status_text += "К сожалению, ставок не было.\n"
                status_text += "Аукцион завершен без продажи."
                
                # Уведомляем продавца
                try:
                    # Проверяем подписку продавца перед созданием ссылки на пост
                    seller_subscribed = await self.check_user_subscription(owner_id)
                    
                    keyboard_buttons = []
                    if seller_subscribed and channel_message_id:
                        # Создаем ссылку на пост аукциона только если пользователь подписан
                        # Используем username канала для ссылок
                        auction_link = f"https://t.me/{CHANNEL_USERNAME_LINK}/{channel_message_id}"
                        
                        keyboard_buttons.append([InlineKeyboardButton(text="🔗 Перейти к посту", url=auction_link)])
                    elif not seller_subscribed:
                        # Если продавец не подписан, предлагаем подписаться
                        keyboard_buttons.append([InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{self.channel_username.replace('@', '')}")])
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons) if keyboard_buttons else None
                    
                    await self.bot.send_message(
                        chat_id=owner_id,
                        text=f"⏰ <b>Аукцион завершен</b>\n\n"
                             f"Ваш лот <b>{description}</b> завершен без ставок.\n\n"
                             f"Вы можете создать новый аукцион.",
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logging.warning(f"Failed to notify owner {owner_id}: {e}")
            
            # Обновляем сообщение в канале (без кнопки истории ставок)
            if channel_chat_id and channel_message_id:
                try:
                    # Обновляем сообщение без клавиатуры
                    await self.bot.edit_message_text(
                        chat_id=channel_chat_id,
                        message_id=channel_message_id,
                        text=status_text
                    )
                    
                except Exception as e:
                    logging.error(f"Failed to update channel message: {e}")
            
            # История ставок теперь отправляется через кнопку в сообщении о продаже
                    
        except Exception as e:
            logging.error(f"Error finalizing auction {auction.get('id', 'unknown')}: {e}")


    async def get_auction_time_left(self, end_time) -> str:
        """Получить оставшееся время до окончания аукциона"""
        # Преобразуем строку в datetime если необходимо
        if isinstance(end_time, str):
            try:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                # Если не удается распарсить, возвращаем ошибку
                return "Ошибка времени"
        
        now = datetime.now()
        if end_time <= now:
            return "Завершен"
            
        delta = end_time - now
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}д {hours}ч {minutes}м"
        elif hours > 0:
            return f"{hours}ч {minutes}м"
        else:
            return f"{minutes}м"

    async def format_auction_text(self, auction: Dict, show_buttons: bool = True) -> tuple[str, InlineKeyboardMarkup]:
        """Форматировать текст аукциона"""
        time_left = await self.get_auction_time_left(auction['end_time'])
        
        text = f"<b>{auction['description']}</b>\n\n"
        text += f"<b>Стартовая цена:</b> {auction['start_price']} ₽\n"
        
        if auction['blitz_price']:
            text += f"<b>Блиц-цена:</b> {auction['blitz_price']} ₽\n"
            
        text += "———————————————\n"
        text += f"<b>Текущая ставка:</b> {auction['current_price']} ₽\n"
        
        if auction['current_leader_username'] and auction.get('current_leader_id'):
            # Создаем кликабельную ссылку на лидера
            leader_link = f"<a href='tg://user?id={auction['current_leader_id']}'>@{auction['current_leader_username']}</a>"
            text += f"<b>Лидер:</b> {leader_link}\n"
        elif auction['current_leader_username']:
            text += f"<b>Лидер:</b> @{auction['current_leader_username']}\n"
        else:
            text += f"<b>Лидер:</b> -\n"
            
        # Преобразуем end_time в datetime если это строка
        end_time = auction['end_time']
        if isinstance(end_time, str):
            try:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                end_time = datetime.now()  # Fallback
        
        text += f"<b>Окончание:</b> {end_time.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"<b>Осталось:</b> {time_left}\n\n"
        
        if auction['status'] == 'active':
            text += "⚠️Товар продаётся по принципу аукциона! Возврату не подлежит!"
        elif auction['status'] == 'sold':
            text += "✅ <b>ПРОДАНО</b>"
        elif auction['status'] == 'expired':
            text += "⏰ <b>ЗАВЕРШЕН</b>"
        
        # Создаем клавиатуру
        keyboard = None
        if show_buttons and auction['status'] == 'active':
            from bot import get_bidding_keyboard
            keyboard = get_bidding_keyboard(auction['blitz_price'])
        # Убираем кнопку истории ставок из публичного доступа
        
        return text, keyboard
