# 🚀 Развертывание сервера платежей

## 🎯 Проблема решена!

Ваш сервер платежей работает локально, но недоступен из интернета. Вот несколько способов решения:

## 🔧 Вариант 1: Railway (Рекомендуется)

### 1. Создайте аккаунт
- Перейдите на https://railway.app
- Войдите через GitHub

### 2. Создайте проект
- Нажмите "New Project"
- Выберите "Deploy from GitHub repo"
- Подключите ваш репозиторий

### 3. Настройте переменные
В разделе "Variables" добавьте:
```
YOOMONEY_RECEIVER=4100118987681575
YOOMONEY_SECRET=SaTKEuJWPVXJl/JFpXDCHZ4q
YOOMONEY_NOTIFICATION_URL=https://your-app.railway.app/yoomoney
```

### 4. Деплой
- Railway автоматически развернет приложение
- Получите URL: `https://your-app.railway.app`

## 🔧 Вариант 2: Heroku

### 1. Установите Heroku CLI
```bash
# Скачайте с https://devcenter.heroku.com/articles/heroku-cli
# Или используйте winget:
winget install Heroku.HerokuCLI
```

### 2. Войдите в аккаунт
```bash
heroku login
```

### 3. Создайте приложение
```bash
heroku create your-auction-bot
```

### 4. Настройте переменные
```bash
heroku config:set YOOMONEY_RECEIVER=4100118987681575
heroku config:set YOOMONEY_SECRET=SaTKEuJWPVXJl/JFpXDCHZ4q
heroku config:set YOOMONEY_NOTIFICATION_URL=https://your-auction-bot.herokuapp.com/yoomoney
```

### 5. Деплой
```bash
git add .
git commit -m "Deploy payment server"
git push heroku main
```

## 🔧 Вариант 3: VPS

### 1. Арендуйте VPS
- DigitalOcean: от $5/месяц
- Vultr: от $3.50/месяц
- Hetzner: от €3.50/месяц

### 2. Подключитесь к серверу
```bash
ssh root@your-server-ip
```

### 3. Установите зависимости
```bash
apt update
apt install python3 python3-pip git
```

### 4. Клонируйте проект
```bash
git clone <your-repo>
cd auction-bot
pip3 install -r requirements.txt
```

### 5. Запустите сервер
```bash
python3 start_payment_server.py
```

## 🔧 Вариант 4: Локальный туннель (временное решение)

### 1. Установите localtunnel
```bash
npm install -g localtunnel
```

### 2. Запустите туннель
```bash
lt --port 8080 --subdomain auction-bot
```

### 3. Получите URL
- URL: `https://auction-bot.loca.lt`
- Webhook: `https://auction-bot.loca.lt/yoomoney`

## 🧪 Тестирование

После развертывания любого варианта:

```bash
python test_webhook.py https://your-domain.com
```

## 📋 Настройка в ЮMoney

1. **Войдите в личный кабинет ЮMoney**
2. **Перейдите в "Уведомления"**
3. **Добавьте URL уведомлений:**
   ```
   https://your-domain.com/yoomoney
   ```
4. **Укажите секретное слово:**
   ```
   SaTKEuJWPVXJl/JFpXDCHZ4q
   ```

## 🎉 Результат

После настройки:
- ✅ Сервер доступен из интернета
- ✅ ЮMoney может отправлять уведомления
- ✅ Платежи обрабатываются автоматически
- ✅ Публикации начисляются пользователям

## 📞 Поддержка

Если что-то не работает:
1. Проверьте логи приложения
2. Убедитесь в правильности URL
3. Проверьте переменные окружения
4. Обратитесь к администратору

---

**Рекомендация:** Используйте Railway - это самый простой способ! 🚀
