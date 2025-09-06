# Развертывание бота на Railway

## Подготовка к развертыванию

### 1. Файлы уже готовы:
- ✅ `Procfile` - указывает Railway как запускать приложение
- ✅ `requirements.txt` - список зависимостей Python
- ✅ `bot.py` - основной файл бота с webhook

### 2. Переменные окружения

Создайте файл `.env` с переменными окружения:

```env
BOT_TOKEN=8486386170:AAEGHCYOtGlx3TrmZ3e9vQ7p8PbtCgs0YMw
YOOMONEY_RECEIVER=4100118987681575
YOOMONEY_SECRET=SaTKEuJWPVXJI/JFpXDCHZ4q
YOOMONEY_NOTIFICATION_URL=https://telegabot-production-3c68.up.railway.app/yoomoney
CHANNEL_USERNAME=-1002369805353
CHANNEL_USERNAME_LINK=baraxolkavspb
CHANNEL_DISPLAY_NAME=Барахолка СПБ
ADMIN_USER_IDS=476589798
DATABASE_PATH=auction_bot.db
DISABLE_SUBSCRIPTION_CHECK=true
```

## Развертывание на Railway

### 1. Подключение к GitHub

1. Зайдите на [Railway](https://railway.app/)
2. Войдите в аккаунт
3. Нажмите "New Project"
4. Выберите "Deploy from GitHub repo"
5. Подключите ваш репозиторий с ботом

### 2. Настройка переменных окружения

1. В панели Railway выберите ваш проект
2. Перейдите в раздел "Variables"
3. Добавьте все переменные из `.env` файла:
   - `BOT_TOKEN`
   - `YOOMONEY_RECEIVER`
   - `YOOMONEY_SECRET`
   - `YOOMONEY_NOTIFICATION_URL`
   - `CHANNEL_USERNAME`
   - `CHANNEL_USERNAME_LINK`
   - `CHANNEL_DISPLAY_NAME`
   - `ADMIN_USER_IDS`
   - `DATABASE_PATH`
   - `DISABLE_SUBSCRIPTION_CHECK`

### 3. Настройка домена

1. В разделе "Settings" → "Domains"
2. Railway автоматически создаст домен вида: `https://your-app-name.up.railway.app`
3. Скопируйте этот URL и обновите `YOOMONEY_NOTIFICATION_URL` в переменных окружения

### 4. Развертывание

1. Railway автоматически начнет развертывание при push в репозиторий
2. Следите за логами в разделе "Deployments"
3. После успешного развертывания бот будет доступен по URL

## Проверка развертывания

### 1. Health Check

```bash
curl https://your-app-name.up.railway.app/health
```

Ожидаемый ответ:
```json
{"status": "ok", "message": "Auction bot is running"}
```

### 2. YooMoney Webhook Test

```bash
curl https://your-app-name.up.railway.app/yoomoney/test
```

Ожидаемый ответ:
```json
{
  "status": "ok",
  "message": "YooMoney webhook is ready",
  "webhook_url": "https://your-app-name.up.railway.app/yoomoney",
  "receiver": "4100118987681575"
}
```

## Настройка YooMoney

После успешного развертывания:

1. Зайдите в [YooMoney](https://yoomoney.ru/)
2. Перейдите в "Настройки" → "HTTP-уведомления"
3. Укажите URL: `https://your-app-name.up.railway.app/yoomoney`
4. Укажите секрет: `SaTKEuJWPVXJI/JFpXDCHZ4q`
5. Включите уведомления
6. Нажмите "Протестировать"

## Мониторинг

### Логи

В панели Railway:
1. Перейдите в раздел "Deployments"
2. Выберите последний деплой
3. Нажмите "View Logs"

### Метрики

Railway показывает:
- CPU использование
- Память
- Сетевой трафик
- Время отклика

## Обновление бота

Для обновления бота:
1. Внесите изменения в код
2. Сделайте commit и push в GitHub
3. Railway автоматически пересоберет и развернет новую версию

## Устранение неполадок

### Бот не запускается

1. Проверьте логи в Railway
2. Убедитесь, что все переменные окружения установлены
3. Проверьте синтаксис Python кода

### Webhook не работает

1. Убедитесь, что URL правильный
2. Проверьте, что бот отвечает на `/health`
3. Проверьте настройки в YooMoney

### База данных

Railway предоставляет встроенную PostgreSQL, но бот использует SQLite файл.
Для продакшена рекомендуется:
1. Подключить PostgreSQL
2. Обновить код для работы с PostgreSQL
3. Или использовать внешнее хранилище для SQLite файла

## Безопасность

### Переменные окружения

Никогда не коммитьте файл `.env` в репозиторий!
Добавьте в `.gitignore`:
```
.env
*.db
__pycache__/
```

### Секретные ключи

Все секретные данные должны быть в переменных окружения Railway, а не в коде.
