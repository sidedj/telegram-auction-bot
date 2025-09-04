# 🌐 Настройка платежей через локальную сеть

## 📋 Проблема с ngrok

ngrok заблокирован антивирусом, поэтому используем альтернативные решения.

## 🔧 Решение 1: Проброс портов в роутере

### 1. Настройка роутера

1. **Войдите в настройки роутера:**
   - Обычно: http://192.168.1.1 или http://192.168.0.1
   - Логин/пароль: admin/admin или admin/password

2. **Найдите раздел "Port Forwarding" или "Проброс портов"**

3. **Добавьте правило:**
   ```
   Внешний порт: 5000
   Внутренний IP: 192.168.0.107
   Внутренний порт: 5000
   Протокол: TCP
   ```

4. **Сохраните настройки**

### 2. Обновление конфигурации

URL уведомлений: `http://212.111.81.230:5000/yoomoney`

### 3. Настройка в ЮMoney

1. Войдите в личный кабинет ЮMoney
2. Перейдите в "Уведомления"
3. Укажите URL: `http://212.111.81.230:5000/yoomoney`
4. Секретное слово: `SaTKEuJWPVXJl/JFpXDCHZ4q`

## 🔧 Решение 2: Использование VPS

### 1. Аренда VPS

Рекомендуемые провайдеры:
- **DigitalOcean** - от $5/месяц
- **Vultr** - от $3.50/месяц
- **Hetzner** - от €3.50/месяц

### 2. Развертывание на VPS

```bash
# Установка Python и зависимостей
sudo apt update
sudo apt install python3 python3-pip git

# Клонирование проекта
git clone <your-repo>
cd auction-bot

# Установка зависимостей
pip3 install -r requirements.txt

# Настройка systemd сервиса
sudo nano /etc/systemd/system/auction-bot.service
```

### 3. Конфигурация systemd

```ini
[Unit]
Description=Auction Bot Payment Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/auction-bot
ExecStart=/usr/bin/python3 start_payment_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Запуск сервиса

```bash
sudo systemctl enable auction-bot
sudo systemctl start auction-bot
```

## 🔧 Решение 3: Использование Heroku

### 1. Создание Procfile

```
web: python start_payment_server.py
```

### 2. Настройка переменных окружения

```bash
heroku config:set YOOMONEY_RECEIVER=4100118987681575
heroku config:set YOOMONEY_SECRET=SaTKEuJWPVXJl/JFpXDCHZ4q
heroku config:set YOOMONEY_NOTIFICATION_URL=https://your-app.herokuapp.com/yoomoney
```

### 3. Деплой

```bash
git add .
git commit -m "Deploy payment server"
git push heroku main
```

## 🔧 Решение 4: Использование Railway

### 1. Подключение к Railway

```bash
npm install -g @railway/cli
railway login
railway init
```

### 2. Настройка переменных

```bash
railway variables set YOOMONEY_RECEIVER=4100118987681575
railway variables set YOOMONEY_SECRET=SaTKEuJWPVXJl/JFpXDCHZ4q
```

### 3. Деплой

```bash
railway up
```

## 🧪 Тестирование

После настройки любого из решений:

```bash
python test_webhook.py https://your-domain.com
```

## ⚠️ Важные моменты

### Безопасность
- Используйте HTTPS для продакшена
- Настройте файрвол
- Регулярно обновляйте зависимости

### Мониторинг
- Настройте логирование
- Используйте мониторинг сервисов
- Создайте резервные копии

### Резервные планы
- Настройте несколько способов получения уведомлений
- Используйте очереди сообщений
- Создайте fallback механизмы

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи сервера
2. Убедитесь в правильности настроек
3. Проверьте доступность из интернета
4. Обратитесь к администратору

---

**Рекомендация:** Для продакшена используйте VPS с HTTPS!
