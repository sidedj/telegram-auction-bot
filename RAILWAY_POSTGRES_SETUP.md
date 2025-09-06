# Настройка PostgreSQL на Railway

## 1. Добавление PostgreSQL в Railway

1. Войдите в [Railway Dashboard](https://railway.app/dashboard)
2. Выберите ваш проект
3. Нажмите **"+ New"** → **"Database"** → **"PostgreSQL"**
4. Дождитесь создания базы данных

## 2. Получение DATABASE_URL

1. В Railway Dashboard выберите созданную PostgreSQL базу данных
2. Перейдите на вкладку **"Variables"**
3. Скопируйте значение **DATABASE_URL** (выглядит как `postgresql://...`)

## 3. Настройка переменных окружения

1. В Railway Dashboard выберите ваш сервис бота
2. Перейдите на вкладку **"Variables"**
3. Добавьте переменную:
   - **Name**: `DATABASE_URL`
   - **Value**: скопированный URL из шага 2

## 4. Обновление кода

Код уже обновлен для работы с PostgreSQL:
- ✅ `database_postgres.py` - новый модуль для PostgreSQL
- ✅ `requirements.txt` - добавлен `asyncpg` и `quart`
- ✅ `bot.py` - обновлен для использования PostgreSQL

## 5. Развертывание

1. Закоммитьте изменения:
   ```bash
   git add .
   git commit -m "Add PostgreSQL support"
   git push
   ```

2. Railway автоматически пересоберет и развернет приложение

## 6. Проверка работы

1. Проверьте логи в Railway Dashboard
2. Убедитесь, что база данных инициализирована
3. Протестируйте webhook: `https://your-app.up.railway.app/yoomoney/test`

## 7. Преимущества PostgreSQL на Railway

- ✅ **Единая база данных** для webhook и бота
- ✅ **Автоматическое начисление** платежей
- ✅ **Масштабируемость** и надежность
- ✅ **Резервное копирование** автоматически
- ✅ **Мониторинг** и логи

## 8. Миграция данных (если нужно)

Если у вас есть данные в SQLite, их можно перенести:

1. Экспортируйте данные из SQLite
2. Импортируйте в PostgreSQL
3. Или начните с чистой базы данных

## Готово! 🎉

Теперь платежи будут работать автоматически через единую базу данных PostgreSQL на Railway!
