# Настройка YooMoney для бота аукционов

## Обзор

Бот интегрирован с YooMoney для обработки платежей на пополнение баланса. Пользователи могут покупать публикации для создания аукционов.

## Настройка в YooMoney

### 1. Получение данных для интеграции

1. Войдите в [YooMoney](https://yoomoney.ru/)
2. Перейдите в раздел "Настройки" → "HTTP-уведомления"
3. Скопируйте следующие данные:
   - **Номер кошелька** (receiver): `4100118987681575`
   - **Секретный ключ** (secret): `SaTKEuJWPVXJI/JFpXDCHZ4q`

### 2. Настройка HTTP-уведомлений

1. В разделе "HTTP-уведомления" укажите:
   - **URL для уведомлений**: `https://telegabot-production-3c68.up.railway.app/yoomoney`
   - **Секрет для проверки подлинности**: `SaTKEuJWPVXJI/JFpXDCHZ4q`
2. Включите опцию "Отправлять HTTP-уведомления"
3. Нажмите "Протестировать" для проверки подключения
4. Нажмите "Готово" для сохранения настроек

## Тарифы

| Количество публикаций | Цена | Описание |
|----------------------|------|----------|
| 1 | 50₽ | 1 публикация |
| 5 | 200₽ | 5 публикаций |
| 10 | 350₽ | 10 публикаций |
| 20 | 600₽ | 20 публикаций |

## Как работает интеграция

### 1. Генерация ссылки на оплату

Когда пользователь выбирает тариф, бот генерирует ссылку вида:
```
https://yoomoney.ru/quickpay/confirm.xml?receiver=4100118987681575&quickpay-form=shop&targets=1 публикация&sum=50&label=user_123456789
```

Где:
- `receiver` - номер кошелька
- `targets` - описание товара
- `sum` - сумма к оплате
- `label` - ID пользователя в формате `user_123456789`

### 2. Обработка платежа

1. Пользователь переходит по ссылке и оплачивает
2. YooMoney отправляет уведомление на webhook
3. Бот проверяет подпись и валидность платежа
4. Начисляет публикации на баланс пользователя
5. Отправляет уведомление пользователю

### 3. Webhook endpoint

**URL**: `https://telegabot-production-3c68.up.railway.app/yoomoney`
**Метод**: POST
**Формат**: application/x-www-form-urlencoded

## Безопасность

### Проверка подписи

Webhook проверяет подпись уведомления для защиты от подделок:

```python
check_string = f"{notification_type}&{operation_id}&{amount}&{currency}&{datetime}&{sender}&{codepro}&{secret}&{label}"
calculated_hash = hashlib.sha1(check_string.encode()).hexdigest()
```

### Защита от дублирования

Бот отслеживает обработанные платежи по `operation_id` в таблице `processed_payments`.

## Мониторинг

### Логи

Все операции логируются с уровнем INFO:
- Получение уведомлений
- Обработка платежей
- Начисление баланса
- Ошибки

### Команды бота

- `/payment_status` - показать статус платежей и историю транзакций
- `/top_up` - пополнить баланс

### Health check

**URL**: `https://telegabot-production-3c68.up.railway.app/health`
**URL теста**: `https://telegabot-production-3c68.up.railway.app/yoomoney/test`

## Тестирование

Запустите тестовый скрипт:

```bash
python test_yoomoney_webhook.py
```

Скрипт проверит:
1. Доступность webhook
2. Обработку тестовых уведомлений
3. Симуляцию реальных платежей

## Устранение неполадок

### Платеж не обрабатывается

1. Проверьте логи бота
2. Убедитесь, что webhook URL правильный
3. Проверьте настройки в YooMoney
4. Убедитесь, что платеж не был обработан ранее

### Ошибка подписи

1. Проверьте правильность секретного ключа
2. Убедитесь, что YooMoney отправляет `sha1_hash`

### Пользователь не получает уведомления

1. Проверьте, что бот может отправлять сообщения пользователю
2. Убедитесь, что пользователь не заблокировал бота

## Конфигурация

Настройки в `config.py`:

```python
YOOMONEY_RECEIVER = "4100118987681575"
YOOMONEY_SECRET = "SaTKEuJWPVXJI/JFpXDCHZ4q"
YOOMONEY_NOTIFICATION_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"
```

## База данных

### Таблица processed_payments

```sql
CREATE TABLE processed_payments (
    operation_id TEXT PRIMARY KEY,
    user_id INTEGER,
    amount REAL,
    publications INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица transactions

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
