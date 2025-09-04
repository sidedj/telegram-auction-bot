# 🚀 Настройка ngrok для платежей ЮMoney

## 📋 Что нужно сделать

### 1. Установка ngrok

1. **Скачайте ngrok:** https://ngrok.com/download
2. **Распакуйте** в папку проекта или добавьте в PATH
3. **Зарегистрируйтесь** на https://ngrok.com и получите токен

### 2. Настройка токена

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### 3. Запуск туннеля

**В отдельном терминале** (не закрывайте его!):

```bash
ngrok http 5000
```

Вы увидите что-то вроде:
```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5000
```

### 4. Обновление конфигурации

Скопируйте URL из ngrok (например: `https://abc123.ngrok-free.app`) и обновите `config.py`:

```python
YOOMONEY_NOTIFICATION_URL = "https://abc123.ngrok-free.app/yoomoney"
```

### 5. Настройка в ЮMoney

1. **Войдите в личный кабинет ЮMoney**
2. **Перейдите в "Уведомления"**
3. **Добавьте URL уведомлений:**
   ```
   https://abc123.ngrok-free.app/yoomoney
   ```
4. **Укажите секретное слово:** `SaTKEuJWPVXJl/JFpXDCHZ4q`

### 6. Тестирование

```bash
python test_webhook.py https://abc123.ngrok-free.app
```

## ⚠️ Важные моменты

### Ngrok бесплатный план:
- **Туннель работает только пока запущен ngrok**
- **URL меняется при каждом перезапуске**
- **Ограничение на количество запросов**

### Для продакшена:
- Используйте **платный план ngrok** или **VPS**
- Настройте **постоянный домен**
- Используйте **HTTPS сертификат**

## 🔧 Устранение проблем

### Ошибка "endpoint is offline"
- Убедитесь, что ngrok запущен
- Проверьте, что сервер платежей работает на порту 5000

### Ошибка "tunnel not found"
- Перезапустите ngrok
- Обновите URL в настройках

### Ошибка 404
- Проверьте, что URL заканчивается на `/yoomoney`
- Убедитесь, что сервер платежей запущен

## 📝 Команды для быстрого запуска

```bash
# Терминал 1: Запуск сервера платежей
python start_payment_server.py

# Терминал 2: Запуск ngrok
ngrok http 5000

# Терминал 3: Тестирование
python test_webhook.py https://YOUR_NGROK_URL.ngrok-free.app
```

## 🎯 Результат

После настройки:
1. ✅ Сервер платежей работает локально
2. ✅ Ngrok туннель активен
3. ✅ ЮMoney может отправлять уведомления
4. ✅ Платежи обрабатываются автоматически
5. ✅ Публикации начисляются пользователям

---

**Готово!** Теперь ваша система платежей полностью функциональна! 🎉
