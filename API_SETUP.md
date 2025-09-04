# 🔌 Настройка API для бота аукционов

## Обзор

Ваш бот аукционов уже настроен для работы с Telegram API через aiogram. Дополнительно добавлена поддержка внешних API для расширенной функциональности.

## 🚀 Быстрая настройка

### 1. Создайте файл `.env`

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# Настройки бота
BOT_TOKEN=ваш_токен_бота
PAYMENTS_PROVIDER_TOKEN=ваш_токен_платежей

# Настройки канала
CHANNEL_USERNAME=-1002369805353
CHANNEL_USERNAME_LINK=baraxolkavspb
CHANNEL_DISPLAY_NAME=Барахолка СПБ

# Администраторы (через запятую)
ADMIN_USER_IDS=476589798

# База данных
DATABASE_PATH=auction_bot.db

# Внешние API (настройте по необходимости)
EXTERNAL_API_URL=https://api.example.com
EXTERNAL_API_KEY=your_api_key_here
EXTERNAL_API_TIMEOUT=30

# IP-адреса для доступа к API (IPv4 и IPv6 через запятую)
# Примеры:
# API_ALLOWED_IPS=192.168.1.100,10.0.0.50,2001:db8::1
# API_ALLOWED_IPS=192.168.0.0/16,10.0.0.0/8
API_ALLOWED_IPS=

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Настройки персистентности
PERSISTENCE_FILE=auction_state.json
PERSISTENCE_INTERVAL=300
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

## 🔧 Настройка внешних API

### IP-адреса для доступа к API

Ваш бот поддерживает ограничение доступа к API по IP-адресам. Это повышает безопасность, позволяя обращаться только к доверенным серверам.

#### Форматы IP-адресов:

- **Отдельные IPv4**: `192.168.1.100`, `10.0.0.50`
- **Отдельные IPv6**: `2001:db8::1`, `::1`
- **Подсети IPv4**: `192.168.0.0/16`, `10.0.0.0/8`
- **Подсети IPv6**: `2001:db8::/32`

#### Примеры настройки:

```env
# Только конкретные IP-адреса
API_ALLOWED_IPS=192.168.1.100,10.0.0.50,2001:db8::1

# Подсети (все IP в диапазоне)
API_ALLOWED_IPS=192.168.0.0/16,10.0.0.0/8

# Смешанный формат
API_ALLOWED_IPS=192.168.1.100,10.0.0.0/8,2001:db8::1

# Без ограничений (пустая строка)
API_ALLOWED_IPS=
```

### Базовый API клиент

Создан универсальный API клиент в `api_client.py`:

- **APIClient** - базовый класс для HTTP запросов
- **AuctionAPIClient** - специализированный клиент для аукционов
- **NotificationAPIClient** - клиент для уведомлений
- **PaymentAPIClient** - клиент для платежей

### Интеграция с ботом

В `api_integration.py` создан класс `APIIntegration` для интеграции с внешними API:

```python
from api_integration import api_integration

# Синхронизация аукциона
await api_integration.sync_auction_to_external(auction_data)

# Отправка уведомления
await api_integration.send_external_notification(user_id, message)

# Обработка платежа
payment_data = await api_integration.process_external_payment(amount, currency, description, user_id)
```

## 📡 Доступные API

### 1. Telegram Bot API (уже настроен)

Ваш бот использует Telegram Bot API через aiogram:

- Отправка сообщений
- Обработка callback'ов
- Работа с медиа
- Платежи (если настроен PAYMENTS_PROVIDER_TOKEN)

### 2. Внешние API (опционально)

Вы можете подключить любые внешние API:

- **API аукционов** - для синхронизации данных
- **API уведомлений** - для отправки уведомлений
- **API платежей** - для обработки платежей
- **API аналитики** - для сбора статистики

## 🛠️ Примеры использования

### Создание аукциона с синхронизацией

```python
# В bot.py, в функции создания аукциона
auction_id = await db.create_auction(...)

# Синхронизируем с внешним API
auction_data = {
    "id": auction_id,
    "description": description,
    "start_price": start_price,
    "blitz_price": blitz_price,
    "owner_id": user_id
}
await api_integration.sync_auction_to_external(auction_data)
```

### Отправка уведомлений

```python
# После завершения аукциона
await api_integration.send_external_notification(
    user_id=winner_id,
    message=f"Поздравляем! Вы выиграли аукцион: {auction_description}",
    notification_type="success"
)
```

### Обработка платежей

```python
# При пополнении баланса
payment_data = await api_integration.process_external_payment(
    amount=amount,
    currency="RUB",
    description=f"Пополнение баланса на {amount} публикаций",
    user_id=user_id
)
```

## 🔒 Безопасность

### Переменные окружения

- Никогда не коммитьте файл `.env` в репозиторий
- Используйте сильные API ключи
- Регулярно обновляйте ключи

### IP-адреса и безопасность

- **Ограничение доступа**: Настройте `API_ALLOWED_IPS` для доступа только к доверенным серверам
- **Проверка подсетей**: Используйте CIDR нотацию для блоков IP-адресов
- **Логирование**: Все попытки доступа к неразрешенным IP логируются
- **Валидация**: IP-адреса проверяются перед каждым запросом к API

### Валидация данных

- Все данные валидируются перед отправкой в API
- Используется таймаут для запросов
- Обработка ошибок на всех уровнях

## 📊 Мониторинг

### Логирование

Все API запросы логируются:

```python
logging.info(f"API Request: {method} {url}")
logging.info(f"API Response Status: {response.status}")
```

### Проверка здоровья

```python
# Проверка доступности API
if await api_integration.health_check():
    print("API доступен")
else:
    print("API недоступен")
```

## 🚨 Устранение неполадок

### API недоступен

1. Проверьте URL и ключ в `.env`
2. Убедитесь, что API сервер запущен
3. Проверьте сетевые настройки

### Ошибки аутентификации

1. Проверьте правильность API ключа
2. Убедитесь, что ключ не истек
3. Проверьте права доступа

### Таймауты

1. Увеличьте `EXTERNAL_API_TIMEOUT` в `.env`
2. Проверьте производительность API сервера
3. Оптимизируйте запросы

## 📝 Дополнительные настройки

### Кастомные заголовки

В `api_client.py` можно добавить кастомные заголовки:

```python
def _get_headers(self) -> Dict[str, str]:
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'AuctionBot/1.0',
        'X-Custom-Header': 'value'  # Добавьте свои заголовки
    }
```

### Обработка ошибок

Добавьте специфичную обработку ошибок:

```python
try:
    result = await client.get('/endpoint')
except APIClientError as e:
    if "404" in str(e):
        # Обработка 404
        pass
    elif "500" in str(e):
        # Обработка 500
        pass
```

## 🎯 Следующие шаги

1. **Настройте `.env`** с вашими API данными
2. **Протестируйте подключение** с помощью `python api_integration.py`
3. **Интегрируйте в бот** нужные API вызовы
4. **Настройте мониторинг** и логирование
5. **Документируйте** ваши API endpoints

---

**Готово!** Ваш бот теперь готов для работы с внешними API. 🚀
