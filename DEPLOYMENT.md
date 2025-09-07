# 🚀 Инструкция по развертыванию на Railway

## 1. Подготовка проекта

Проект уже подготовлен для развертывания на Railway:
- ✅ Создан `.gitignore` файл
- ✅ Настроен `Procfile` для Railway
- ✅ Обновлен `Dockerfile` для webhook режима
- ✅ Создан `env.example` с примерами переменных окружения

## 2. Создание репозитория на GitHub

1. Перейдите на [GitHub.com](https://github.com)
2. Нажмите "New repository"
3. Дайте название: `telegram-auction-bot`
4. Выберите приватный или публичный репозиторий
5. **НЕ** инициализируйте с README, .gitignore или лицензией
6. Нажмите "Create repository"

## 3. Загрузка кода на GitHub

После создания репозитория выполните команды (замените `your-username` на ваш GitHub username):

```bash
git remote add origin https://github.com/your-username/telegram-auction-bot.git
git branch -M main
git push -u origin main
```

## 4. Настройка Railway

### 4.1 Создание проекта на Railway

1. Перейдите на [Railway.app](https://railway.app)
2. Войдите через GitHub
3. Нажмите "New Project"
4. Выберите "Deploy from GitHub repo"
5. Выберите ваш репозиторий `telegram-auction-bot`
6. Railway автоматически определит Python проект

### 4.2 Настройка переменных окружения

В настройках проекта Railway добавьте следующие переменные:

#### Обязательные переменные:
```
BOT_TOKEN=ваш_токен_бота_от_BotFather
CHANNEL_USERNAME=@ваш_канал_или_его_id
ADMIN_USER_IDS=ваш_telegram_id,другие_админы
```

#### Настройки ЮMoney (для платежей):
```
YOOMONEY_RECEIVER=ваш_номер_кошелька_юmoney
YOOMONEY_SECRET=ваш_секретный_ключ
YOOMONEY_NOTIFICATION_URL=https://ваш-проект.up.railway.app/yoomoney
```

#### Дополнительные настройки:
```
CHANNEL_USERNAME_LINK=username_канала_без_@
CHANNEL_DISPLAY_NAME=Название канала
DATABASE_PATH=auction_bot.db
LOG_LEVEL=INFO
DISABLE_SUBSCRIPTION_CHECK=false
```

### 4.3 Настройка домена

1. В настройках проекта Railway перейдите в "Settings"
2. В разделе "Domains" добавьте кастомный домен или используйте предоставленный Railway домен
3. Скопируйте URL (например: `https://your-project.up.railway.app`)

### 4.4 Настройка webhook в Telegram

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/setwebhook`
3. Отправьте URL: `https://your-project.up.railway.app/webhook`
4. Проверьте статус командой `/getwebhookinfo`

## 5. Настройка ЮMoney (опционально)

Если используете платежи через ЮMoney:

1. Войдите в [личный кабинет ЮMoney](https://yoomoney.ru)
2. Перейдите в "Настройки" → "HTTP-уведомления"
3. Добавьте URL: `https://your-project.up.railway.app/yoomoney`
4. Укажите секретный ключ (из переменной `YOOMONEY_SECRET`)

## 6. Проверка работы

1. Откройте ваш бот в Telegram
2. Отправьте команду `/start`
3. Проверьте логи в Railway Dashboard
4. Создайте тестовый аукцион

## 7. Мониторинг

- **Логи**: Railway Dashboard → ваш проект → "Deployments" → "View Logs"
- **Метрики**: Railway Dashboard → ваш проект → "Metrics"
- **Переменные**: Railway Dashboard → ваш проект → "Variables"

## 8. Обновление кода

Для обновления кода:

```bash
git add .
git commit -m "Update: описание изменений"
git push origin main
```

Railway автоматически перезапустит приложение с новым кодом.

## 9. Резервное копирование

Railway автоматически создает резервные копии базы данных, но рекомендуется:
- Регулярно экспортировать данные через админ-панель бота
- Сохранять важные файлы состояния

## 10. Troubleshooting

### Бот не отвечает:
- Проверьте переменную `BOT_TOKEN`
- Убедитесь, что webhook настроен правильно
- Проверьте логи в Railway

### Ошибки с базой данных:
- Проверьте права доступа к файлу базы данных
- Убедитесь, что переменная `DATABASE_PATH` корректна

### Проблемы с платежами:
- Проверьте настройки ЮMoney
- Убедитесь, что URL webhook доступен
- Проверьте переменные `YOOMONEY_*`

---

**Готово! Ваш бот теперь работает на Railway! 🎉**
