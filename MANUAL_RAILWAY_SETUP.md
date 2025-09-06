# Ручная настройка Railway для YooMoney интеграции

## Проблема
CLI Railway не может развернуть приложение из-за проблем с компиляцией aiohttp. Нужно настроить вручную через веб-интерфейс.

## Пошаговая инструкция

### 1. Вход в Railway
1. Откройте [Railway](https://railway.app/)
2. Войдите в аккаунт alexnilov93@gmail.com
3. Найдите проект "proactive-enchantment"

### 2. Настройка переменных окружения
В проекте уже настроены переменные:
- ✅ `BOT_TOKEN` = 8486386170:AAEGHCYOtGlx3TrmZ3e9vQ7p8PbtCgs0YMw
- ✅ `YOOMONEY_RECEIVER` = 4100118987681575
- ✅ `YOOMONEY_SECRET` = SaTKEuJWPVXJI/JFpXDCHZ4q
- ✅ `YOOMONEY_NOTIFICATION_URL` = https://telegabot-production-3c68.up.railway.app/yoomoney
- ✅ `CHANNEL_USERNAME` = -1002369805353
- ✅ `CHANNEL_USERNAME_LINK` = baraxolkavspb
- ✅ `CHANNEL_DISPLAY_NAME` = Барахолка СПБ
- ✅ `ADMIN_USER_IDS` = 476589798
- ✅ `DISABLE_SUBSCRIPTION_CHECK` = true

### 3. Развертывание через GitHub
1. Загрузите код в GitHub репозиторий
2. В Railway выберите "Deploy from GitHub repo"
3. Подключите репозиторий
4. Railway автоматически развернет приложение

### 4. Альтернативный способ - прямое развертывание
1. В Railway выберите "Deploy from folder"
2. Загрузите папку с проектом
3. Railway развернет приложение

### 5. Проверка развертывания
После развертывания проверьте:
- Health check: `https://telegabot-production-3c68.up.railway.app/health`
- YooMoney test: `https://telegabot-production-3c68.up.railway.app/yoomoney/test`

## Настройка YooMoney

### 1. Вход в YooMoney
1. Откройте [YooMoney](https://yoomoney.ru/)
2. Войдите в аккаунт

### 2. Настройка HTTP-уведомлений
1. Перейдите в "Настройки" → "HTTP-уведомления"
2. Укажите URL: `https://telegabot-production-3c68.up.railway.app/yoomoney`
3. Укажите секрет: `SaTKEuJWPVXJI/JFpXDCHZ4q`
4. Включите опцию "Отправлять HTTP-уведомления"
5. Нажмите "Протестировать"
6. Нажмите "Готово"

## Тестирование интеграции

### 1. Тест webhook
```bash
curl https://telegabot-production-3c68.up.railway.app/yoomoney/test
```

### 2. Тест платежа
1. Запустите бота: `@baraxolkaspb_bot`
2. Используйте команду `/top_up`
3. Выберите тариф
4. Оплатите через YooMoney
5. Проверьте, что баланс пополнился

## Файлы для развертывания

Убедитесь, что в репозитории есть:
- ✅ `bot.py` - основной файл бота
- ✅ `requirements.txt` - зависимости Python
- ✅ `Procfile` - команда запуска
- ✅ `Dockerfile` - альтернативный способ развертывания
- ✅ `runtime.txt` - версия Python

## Устранение неполадок

### Бот не запускается
1. Проверьте логи в Railway
2. Убедитесь, что все переменные окружения установлены
3. Проверьте синтаксис Python кода

### Webhook не работает
1. Убедитесь, что URL правильный
2. Проверьте, что бот отвечает на `/health`
3. Проверьте настройки в YooMoney

### Платежи не обрабатываются
1. Проверьте логи бота
2. Убедитесь, что webhook URL правильный
3. Проверьте настройки в YooMoney

## Контакты для поддержки

Если возникнут проблемы:
1. Проверьте логи в Railway
2. Проверьте настройки YooMoney
3. Убедитесь, что все переменные окружения установлены правильно
