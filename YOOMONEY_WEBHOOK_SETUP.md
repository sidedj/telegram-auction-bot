# Настройка уведомлений ЮMoney

## ✅ Что уже настроено

1. **Webhook сервер развернут на Railway**: `https://web-production-fa7dc.up.railway.app`
2. **Endpoint для уведомлений**: `https://web-production-fa7dc.up.railway.app/yoomoney`
3. **Health check**: `https://web-production-fa7dc.up.railway.app/health`
4. **Секрет для проверки**: `SaTKEuJWPVXJI/JFpXDCHZ4q`

## 🔧 Настройка в панели ЮMoney

### Шаг 1: Войти в панель ЮMoney
1. Перейдите на https://yoomoney.ru/
2. Войдите в свой аккаунт
3. Перейдите в раздел "Настройки" → "HTTP-уведомления"

### Шаг 2: Настроить уведомления
1. **URL для уведомлений**: `https://web-production-fa7dc.up.railway.app/yoomoney`
2. **Секрет для проверки подлинности**: `SaTKEuJWPVXJI/JFpXDCHZ4q`
3. **Включить уведомления**: ✅ (галочка должна быть поставлена)

### Шаг 3: Протестировать настройки
1. Нажмите кнопку "Протестировать" рядом с URL
2. Должен прийти ответ "ok" (статус 200)

## 🧪 Тестирование

### Автоматический тест
```bash
python test_yoomoney_webhook.py
```

### Ручной тест через curl
```bash
curl -X POST https://web-production-fa7dc.up.railway.app/yoomoney \
  -d "notification_type=p2p-incoming" \
  -d "notification_secret=SaTKEuJWPVXJI/JFpXDCHZ4q" \
  -d "label=user_7647551803" \
  -d "amount=50.00" \
  -d "unaccepted=false"
```

## 📋 Формат уведомлений

ЮMoney отправляет POST запросы с данными:
- `notification_type`: тип уведомления (p2p-incoming)
- `notification_secret`: секрет для проверки
- `label`: метка платежа (формат: user_123456)
- `amount`: сумма платежа
- `unaccepted`: статус операции (false = подтверждена)
- `operation_id`: ID операции
- `datetime`: время операции

## 🔄 Логика обработки

1. **Проверка секрета**: Сравнивается с `YOOMONEY_SECRET`
2. **Проверка статуса**: `unaccepted` должен быть `false`
3. **Извлечение ID пользователя**: Из `label` (формат: `user_123456`)
4. **Определение количества публикаций**:
   - 48-52₽ → 1 публикация
   - 195-205₽ → 5 публикаций
   - 340-360₽ → 10 публикаций
   - 590-610₽ → 20 публикаций
5. **Обновление баланса** в базе данных
6. **Отправка уведомления** пользователю в Telegram

## 🚨 Устранение неполадок

### Сервер не отвечает
- Проверьте статус на Railway: https://railway.com/project/b4654da0-004c-40bb-9cea-9eecaf719295
- Проверьте логи развертывания

### Уведомления не приходят
- Проверьте URL в настройках ЮMoney
- Проверьте секрет
- Убедитесь, что уведомления включены

### Неправильная сумма
- Проверьте диапазоны сумм в коде
- Учитывайте комиссию ЮMoney (около 2-3%)

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи Railway
2. Протестируйте webhook вручную
3. Проверьте настройки в панели ЮMoney
