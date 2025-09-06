#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая система уведомлений через HTTP
"""

import requests
import json
from config import BOT_TOKEN

def send_balance_notification_simple(user_id, amount, publications, new_balance):
    """Простая отправка уведомления через HTTP API"""
    try:
        # URL для отправки сообщения через Telegram Bot API
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        # Текст уведомления
        if amount > 0:
            text = f"💰 <b>Баланс пополнен!</b>\n\n"
            text += f"💳 Сумма: {amount}₽\n"
            text += f"📝 Публикаций: +{publications}\n"
            text += f"💎 Новый баланс: {new_balance} публикаций"
        else:
            text = f"💰 <b>Баланс пополнен!</b>\n\n"
            text += f"📝 Публикаций: +{publications}\n"
            text += f"💎 Новый баланс: {new_balance} публикаций"
        
        # Данные для отправки
        data = {
            'chat_id': user_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        # Отправляем запрос
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Уведомление отправлено пользователю {user_id}")
            return True
        else:
            print(f"❌ Ошибка отправки уведомления: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_simple_notification():
    """Тест простой системы уведомлений"""
    print("🧪 Тест простой системы уведомлений")
    print("=" * 50)
    
    user_id = 476589798
    
    success = send_balance_notification_simple(
        user_id=user_id,
        amount=200.0,
        publications=4,
        new_balance=999999
    )
    
    if success:
        print("✅ Тест прошел успешно!")
        print("💡 Проверьте Telegram - должно прийти уведомление")
    else:
        print("❌ Тест не прошел")

if __name__ == "__main__":
    test_simple_notification()
