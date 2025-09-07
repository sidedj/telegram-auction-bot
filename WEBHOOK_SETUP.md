# Настройка Webhook для локального тестирования

## Проблема
Кнопки в постах не работают, потому что webhook не настроен. Telegram не может отправлять обновления с кнопок на локальный сервер.

## Решение

### Вариант 1: Использование ngrok (рекомендуется)

1. **Установите ngrok:**
   ```bash
   winget install ngrok.ngrok
   ```

2. **Запустите ngrok:**
   ```bash
   ngrok http 8080
   ```

3. **Скопируйте URL** из ngrok (например: `https://abc123.ngrok.io`)

4. **Настройте webhook:**
   ```bash
   python setup_webhook.py
   ```
   Введите URL: `https://abc123.ngrok.io/webhook`

5. **Запустите бота:**
   ```bash
   python launcher.py webhook
   ```

### Вариант 2: Использование Railway

1. **Проверьте статус Railway:**
   ```bash
   python -c "import requests; response = requests.get('https://web-production-fa7dc.up.railway.app/webhook'); print(f'Status: {response.status_code}')"
   ```

2. **Если Railway работает**, настройте webhook:
   ```bash
   python setup_webhook.py
   ```
   Введите URL: `https://web-production-fa7dc.up.railway.app/webhook`

### Вариант 3: Использование другого туннелинг сервиса

Можно использовать:
- **localtunnel**: `npx localtunnel --port 8080`
- **serveo**: `ssh -R 80:localhost:8080 serveo.net`
- **cloudflared**: `cloudflared tunnel --url http://localhost:8080`

## Проверка

После настройки webhook:
1. Создайте аукцион в боте
2. Нажмите кнопку "Опубликовать"
3. Кнопки должны работать корректно

## Отключение webhook

Для отключения webhook:
```bash
curl -X POST "https://api.telegram.org/bot8486386170:AAEGHCYOtGlx3TrmZ3e9vQ7p8PbtCgs0YMw/deleteWebhook"
```
