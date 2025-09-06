# Руководство по исправлению webhook ЮMoney

## Проблема
Webhook ЮMoney возвращает ошибку 400 при получении POST запросов, что приводит к тому, что платежи не обрабатываются автоматически.

## Выполненные исправления

### 1. Исправлена проверка обязательных полей
- Добавлено поле `label` в список обязательных полей
- Улучшена обработка отсутствующих полей
- Добавлено детальное логирование

### 2. Улучшена функция проверки подписи
- Добавлено детальное логирование процесса проверки подписи
- Исправлена обработка поля `label`

### 3. Добавлена команда для ручного зачисления платежей
- Команда `/manual_payment` для администраторов
- Позволяет зачислять средства пользователям вручную
- Отправляет уведомления пользователям

## Использование команды ручного зачисления

### Синтаксис
```
/manual_payment <user_id> <amount> <description>
```

### Примеры
```
/manual_payment 7647551803 1 Ручное пополнение за 50 руб
/manual_payment 123456789 5 Бонус за активность
```

### Права доступа
- Только для администраторов
- Проверка прав выполняется автоматически

## Диагностика webhook'а

### Проверка доступности
```bash
curl -X GET "https://telegabot-production-3c68.up.railway.app/yoomoney"
```

### Тестирование с полными данными
```python
import requests
import hashlib
from datetime import datetime

WEBHOOK_URL = "https://telegabot-production-3c68.up.railway.app/yoomoney"
YOOMONEY_SECRET = "SaTKEuJWPVXJI/JFpXDCHZ4q"

data = {
    'notification_type': 'p2p-incoming',
    'operation_id': 'test123',
    'amount': '50.00',
    'currency': '643',
    'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    'sender': '7647551803',
    'codepro': 'false',
    'label': 'user_7647551803',
    'test_notification': 'true'
}

# Создаем подпись
string_to_sign = f"{data['notification_type']}&{data['operation_id']}&{data['amount']}&{data['currency']}&{data['datetime']}&{data['sender']}&{data['codepro']}&{YOOMONEY_SECRET}&{data['label']}"
data['sha1_hash'] = hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()

response = requests.post(WEBHOOK_URL, data=data)
print(f"Статус: {response.status_code}")
print(f"Ответ: {response.text}")
```

## Альтернативные решения

### 1. Ручное зачисление через команду
Используйте команду `/manual_payment` для зачисления средств пользователям вручную.

### 2. Проверка через баланс-менеджер
```bash
python balance_manager.py view <user_id>
python balance_manager.py add <user_id> <amount> <description>
```

### 3. Мониторинг платежей
Используйте команду `/sync_payments` для просмотра последних обработанных платежей.

## Рекомендации

1. **Немедленно**: Используйте команду `/manual_payment` для зачисления средств пользователям
2. **Краткосрочно**: Мониторьте платежи через команду `/sync_payments`
3. **Долгосрочно**: Исправьте webhook на Railway или настройте альтернативную систему обработки платежей

## Статус исправлений

- ✅ Исправлена проверка полей в webhook'е
- ✅ Добавлено детальное логирование
- ✅ Создана команда ручного зачисления
- ⚠️ Webhook все еще требует дополнительных исправлений на Railway
- ✅ Пользователи могут получать средства через ручное зачисление

## Контакты

При возникновении проблем с платежами:
1. Используйте команду `/manual_payment` для немедленного зачисления
2. Проверьте логи через команду `/sync_payments`
3. Обратитесь к администратору системы
