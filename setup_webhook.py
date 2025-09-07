#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для настройки webhook для локального тестирования
"""

import requests
import os
import time

def setup_webhook():
    """Настраивает webhook для локального тестирования"""
    
    # Токен бота
    BOT_TOKEN = "8486386170:AAEGHCYOtGlx3TrmZ3e9vQ7p8PbtCgs0YMw"
    
    # URL для webhook (замените на ваш ngrok URL)
    webhook_url = input("Введите URL для webhook (например, https://abc123.ngrok.io/webhook): ")
    
    if not webhook_url:
        print("❌ URL не введен")
        return
    
    # Удаляем старый webhook
    print("🗑️ Удаляем старый webhook...")
    delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    response = requests.post(delete_url)
    print(f"Delete response: {response.status_code} - {response.text}")
    
    # Устанавливаем новый webhook
    print(f"🔗 Устанавливаем webhook: {webhook_url}")
    set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {"url": webhook_url}
    response = requests.post(set_url, data=data)
    print(f"Set response: {response.status_code} - {response.text}")
    
    # Проверяем webhook
    print("✅ Проверяем webhook...")
    get_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    response = requests.get(get_url)
    print(f"Webhook info: {response.json()}")

if __name__ == "__main__":
    setup_webhook()
