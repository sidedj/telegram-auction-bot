# 🔧 Устранение проблем с платежами ЮMoney

## ❌ Проблема: Не приходят уведомления от ЮMoney

### 🔍 Диагностика

1. **Проверьте статус сервера платежей:**
   ```bash
   curl http://localhost:5000/health
   ```
   Должен вернуть: `{"status":"ok","timestamp":"..."}`

2. **Проверьте, запущен ли сервер:**
   ```bash
   netstat -an | findstr :5000
   ```
   Должен показать: `TCP    0.0.0.0:5000           0.0.0.0:0              LISTENING`

### 🛠 Решения

## 1. Запуск сервера платежей

Если сервер не запущен:

```bash
# В отдельном терминале
python start_payment_server.py
```

## 2. Настройка публичного доступа

### Вариант A: ngrok (для тестирования)

1. **Скачайте ngrok:** https://ngrok.com/download
2. **Зарегистрируйтесь** и получите токен
3. **Настройте токен:**
   ```bash
   ngrok config add-authtoken YOUR_TOKEN
   ```
4. **Запустите туннель:**
   ```bash
   ngrok http 5000
   ```
5. **Скопируйте публичный URL** (например: `https://abc123.ngrok.io`)
6. **Обновите настройки в ЮMoney:**
   - URL уведомлений: `https://abc123.ngrok.io/yoomoney`
   - Секретное слово: `SaTKEuJWPVXJl/JFpXDCHZ4q`

### Вариант B: VPS/Хостинг (для продакшена)

1. **Разверните сервер** на VPS (DigitalOcean, AWS, etc.)
2. **Настройте домен** и SSL сертификат
3. **Обновите конфигурацию:**
   ```env
   YOOMONEY_NOTIFICATION_URL=https://yourdomain.com/yoomoney
   ```
4. **Настройте в ЮMoney:**
   - URL уведомлений: `https://yourdomain.com/yoomoney`
   - Секретное слово: `SaTKEuJWPVXJl/JFpXDCHZ4q`

### Вариант C: Локальная сеть (только для тестирования)

1. **Узнайте ваш внешний IP:**
   ```bash
   curl ifconfig.me
   ```
2. **Настройте проброс портов** в роутере (порт 5000)
3. **Обновите конфигурацию:**
   ```env
   YOOMONEY_NOTIFICATION_URL=http://YOUR_EXTERNAL_IP:5000/yoomoney
   ```

## 3. Проверка настроек ЮMoney

1. **Войдите в личный кабинет ЮMoney**
2. **Перейдите в "Уведомления"**
3. **Проверьте настройки:**
   - URL: `https://your-domain.com/yoomoney` (или ngrok URL)
   - Секретное слово: `SaTKEuJWPVXJl/JFpXDCHZ4q`
   - Статус: "Активно"

## 4. Тестирование

### Тест 1: Проверка webhook
```bash
curl -X POST http://localhost:5000/yoomoney \
  -d "notification_secret=SaTKEuJWPVXJl/JFpXDCHZ4q" \
  -d "label=user_123456" \
  -d "amount=50.00" \
  -d "operation_id=test_123" \
  -d "unaccepted=false"
```

### Тест 2: Проверка через ngrok
```bash
curl -X POST https://your-ngrok-url.ngrok.io/yoomoney \
  -d "notification_secret=SaTKEuJWPVXJl/JFpXDCHZ4q" \
  -d "label=user_123456" \
  -d "amount=50.00" \
  -d "operation_id=test_123" \
  -d "unaccepted=false"
```

## 5. Мониторинг

### Логи сервера платежей
```bash
tail -f payment_server.log
```

### Логи бота
```bash
tail -f bot.log
```

### Проверка очереди уведомлений
```bash
curl http://localhost:5000/payment-history/USER_ID
```

## 🚨 Частые ошибки

### Ошибка: "Неверный секрет"
- Проверьте `YOOMONEY_SECRET` в config.py
- Убедитесь, что в ЮMoney указан тот же секрет

### Ошибка: "Connection refused"
- Сервер платежей не запущен
- Неправильный URL в настройках ЮMoney

### Ошибка: "Invalid label"
- Label должен быть в формате `user_USER_ID`
- USER_ID должен быть числом

### Ошибка: "Unknown amount"
- Сумма должна соответствовать тарифным планам
- Проверьте `PAYMENT_PLANS` в config.py

## 📞 Поддержка

Если проблема не решается:
1. Проверьте все логи
2. Убедитесь в правильности настроек
3. Протестируйте webhook вручную
4. Обратитесь к администратору

---

**Важно:** Для продакшена обязательно используйте HTTPS и надежный хостинг!
