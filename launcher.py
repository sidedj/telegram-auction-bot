#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Универсальный запускатель бота аукционов
Объединяет все варианты запуска в одном файле
"""

import asyncio
import logging
import sys
import subprocess
import time
import os
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
sys.path.append(str(Path(__file__).parent))

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('auction_bot.log', encoding='utf-8')
        ]
    )

def check_dependencies():
    """Проверка зависимостей"""
    required_modules = [
        'aiogram', 'aiosqlite', 'asyncio', 'datetime', 'json', 'pathlib'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Отсутствуют необходимые модули: {', '.join(missing_modules)}")
        print("Установите их с помощью: pip install -r requirements.txt")
        return False
    
    return True

def is_bot_running():
    """Проверяет, запущен ли бот"""
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        return 'python.exe' in result.stdout
    except:
        return False

def start_bot():
    """Запускает бота"""
    print("🚀 Запуск бота...")
    try:
        # Запускаем бота в фоновом режиме
        process = subprocess.Popen([sys.executable, 'bot.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        print(f"✅ Бот запущен с PID: {process.pid}")
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        return None

def start_webhook_server():
    """Запускает webhook сервер для Railway"""
    print("🌐 Запуск webhook сервера...")
    try:
        from bot import app
        port = int(os.environ.get("PORT", 8080))
        print(f"🌐 Запуск сервера на порту {port}")
        # Используем gunicorn для production
        import gunicorn.app.wsgiapp as wsgi
        sys.argv = ['gunicorn', '--bind', f'0.0.0.0:{port}', '--workers', '1', '--timeout', '120', 'bot:app']
        wsgi.run()
    except ImportError:
        # Если gunicorn не установлен, используем Flask
        print("⚠️ Gunicorn не найден, используем Flask (не рекомендуется для production)")
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        print(f"❌ Ошибка запуска webhook сервера: {e}")

def start_with_persistence():
    """Запуск бота с системой персистентности"""
    print("🚀 Запуск бота аукционов с системой персистентности")
    print("=" * 60)
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    # Настраиваем логирование
    setup_logging()
    
    print("✅ Зависимости проверены")
    print("✅ Логирование настроено")
    print("✅ Система персистентности активирована")
    print("\n🔄 Запуск бота...")
    
    try:
        # Импортируем и запускаем основной цикл бота
        from bot import main
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Получен сигнал остановки")
        print("💾 Сохранение состояния...")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        logging.critical(f"Critical error: {e}")
        sys.exit(1)
    finally:
        print("✅ Бот остановлен")

def start_monitor():
    """Запуск мониторинга бота с автоперезапуском"""
    print("🤖 Автоматический запуск бота")
    print("Нажмите Ctrl+C для остановки")
    print("-" * 40)
    
    bot_process = None
    
    try:
        while True:
            if not is_bot_running():
                print(f"⏰ {time.strftime('%H:%M:%S')} - Бот не запущен, перезапускаем...")
                if bot_process:
                    bot_process.terminate()
                bot_process = start_bot()
            else:
                print(f"✅ {time.strftime('%H:%M:%S')} - Бот работает")
            
            # Проверяем каждые 30 секунд
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Остановка мониторинга...")
        if bot_process:
            bot_process.terminate()
        print("✅ Мониторинг остановлен")

def main():
    """Главная функция с выбором режима запуска"""
    if len(sys.argv) < 2:
        print("🤖 Запускатель бота аукционов")
        print("=" * 40)
        print("Доступные режимы:")
        print("  python launcher.py bot          - Обычный запуск")
        print("  python launcher.py persistence  - С персистентностью")
        print("  python launcher.py webhook      - Webhook сервер")
        print("  python launcher.py monitor      - Мониторинг с автоперезапуском")
        print("=" * 40)
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "bot":
        print("🚀 Обычный запуск бота...")
        from bot import main
        asyncio.run(main())
        
    elif mode == "persistence":
        start_with_persistence()
        
    elif mode == "webhook":
        start_webhook_server()
        
    elif mode == "monitor":
        start_monitor()
        
    else:
        print(f"❌ Неизвестный режим: {mode}")
        print("Доступные режимы: bot, persistence, webhook, monitor")

if __name__ == "__main__":
    main()
