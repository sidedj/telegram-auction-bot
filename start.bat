@echo off
chcp 65001 >nul
title Бот аукционов

echo.
echo ========================================
echo           БОТ АУКЦИОНОВ
echo ========================================
echo.

echo 🔍 Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python найден

echo.
echo 🔍 Проверка зависимостей...
python -c "import aiogram, aiosqlite" >nul 2>&1
if errorlevel 1 (
    echo ❌ Не все зависимости установлены
    echo 📦 Устанавливаем зависимости...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей
        pause
        exit /b 1
    )
)

echo ✅ Зависимости готовы

echo.
echo 🚀 Запуск бота...
echo.
echo 💡 Доступные режимы:
echo    python launcher.py bot          - Обычный запуск
echo    python launcher.py persistence  - С персистентностью
echo    python launcher.py webhook      - Webhook сервер
echo    python launcher.py monitor      - Мониторинг с автоперезапуском
echo.

python launcher.py persistence

echo.
echo ⏹️ Бот остановлен
pause
