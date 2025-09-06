#!/usr/bin/env python3
"""
Модуль для отправки уведомлений пользователям
"""
import logging
from typing import Optional
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

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
            
            # Создаем кнопку для перехода к аукциону
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Мои аукционы", callback_data="my_auctions")]
            ])
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            
            logging.info(f"✅ Уведомление о создании аукциона отправлено пользователю {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка отправки уведомления о создании аукциона пользователю {user_id}: {e}")
            return False
    
    async def send_auction_published_notification(self, user_id: int, auction_description: str, remaining_balance: int, is_admin: bool = False) -> bool:
        """
        Отправляет уведомление о публикации аукциона и списании с баланса
        """
        try:
            message = f"✅ <b>Аукцион опубликован!</b>\n\n"
            message += f"📝 Описание: {auction_description[:100]}{'...' if len(auction_description) > 100 else ''}\n"
            message += f"📢 Аукцион размещен в канале <a href='https://t.me/baraholka_spb'>Барахолка СПБ</a>\n\n"
            
            if is_admin:
                message += f"💎 Осталось публикаций: ∞ (администратор)\n"
            else:
                message += f"💎 Осталось публикаций: {remaining_balance}\n"
                message += f"💸 С баланса списано: 1 публикация\n"
            
            message += f"\n🎯 Аукцион активен и принимает ставки!"
            
            # Создаем кнопки для управления
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Мои аукционы", callback_data="my_auctions")],
                [InlineKeyboardButton(text="💰 Пополнить баланс", callback_data="top_up_balance")]
            ])
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            
            logging.info(f"✅ Уведомление о публикации аукциона отправлено пользователю {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка отправки уведомления о публикации аукциона пользователю {user_id}: {e}")
            return False
    
    async def send_auction_ended_notification(self, user_id: int, auction_description: str, final_price: float, winner_id: int = None) -> bool:
        """
        Отправляет уведомление о завершении аукциона
        """
        try:
            if winner_id and winner_id != user_id:
                # Уведомление для продавца о продаже
                message = f"🎉 <b>Аукцион завершен!</b>\n\n"
                message += f"📝 Лот: {auction_description[:100]}{'...' if len(auction_description) > 100 else ''}\n"
                message += f"💰 Финальная цена: {final_price}₽\n"
                message += f"👤 Покупатель: ID {winner_id}\n\n"
                message += f"✅ Лот успешно продан!"
            else:
                # Уведомление для покупателя о выигрыше
                message = f"🏆 <b>Поздравляем с победой!</b>\n\n"
                message += f"📝 Лот: {auction_description[:100]}{'...' if len(auction_description) > 100 else ''}\n"
                message += f"💰 Ваша ставка: {final_price}₽\n\n"
                message += f"🎯 Свяжитесь с продавцом для завершения сделки!"
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML"
            )
            
            logging.info(f"✅ Уведомление о завершении аукциона отправлено пользователю {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка отправки уведомления о завершении аукциона пользователю {user_id}: {e}")
            return False
    
    async def close(self):
        """Закрывает соединение с ботом"""
        await self.bot.session.close()


# Глобальный экземпляр менеджера уведомлений
notification_manager = None

def init_notifications(bot_token: str):
    """Инициализирует менеджер уведомлений"""
    global notification_manager
    notification_manager = NotificationManager(bot_token)

async def send_balance_notification(user_id: int, amount: float, publications: int, new_balance: int) -> bool:
    """Отправляет уведомление о пополнении баланса"""
    if notification_manager:
        return await notification_manager.send_balance_notification(user_id, amount, publications, new_balance)
    return False

async def send_auction_created_notification(user_id: int, auction_description: str, auction_id: int) -> bool:
    """Отправляет уведомление о создании аукциона"""
    if notification_manager:
        return await notification_manager.send_auction_created_notification(user_id, auction_description, auction_id)
    return False

async def send_auction_published_notification(user_id: int, auction_description: str, remaining_balance: int, is_admin: bool = False) -> bool:
    """Отправляет уведомление о публикации аукциона"""
    if notification_manager:
        return await notification_manager.send_auction_published_notification(user_id, auction_description, remaining_balance, is_admin)
    return False

async def send_auction_ended_notification(user_id: int, auction_description: str, final_price: float, winner_id: int = None) -> bool:
    """Отправляет уведомление о завершении аукциона"""
    if notification_manager:
        return await notification_manager.send_auction_ended_notification(user_id, auction_description, final_price, winner_id)
    return False

async def close_notifications():
    """Закрывает соединение с ботом"""
    if notification_manager:
        await notification_manager.close()
