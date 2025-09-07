# ⚡ Быстрый старт

## 1. Создайте репозиторий на GitHub

1. Перейдите на [GitHub.com](https://github.com)
2. Нажмите "New repository"
3. Название: `telegram-auction-bot`
4. Создайте репозиторий

## 2. Загрузите код

```bash
git remote add origin https://github.com/ВАШ-USERNAME/telegram-auction-bot.git
git branch -M main
git push -u origin main
```

## 3. Настройте Railway

1. Перейдите на [Railway.app](https://railway.app)
2. Войдите через GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Выберите ваш репозиторий

## 4. Добавьте переменные окружения

В Railway Dashboard → Variables добавьте:

```
BOT_TOKEN=ваш_токен_от_BotFather
CHANNEL_USERNAME=@ваш_канал
ADMIN_USER_IDS=ваш_telegram_id
```

## 5. Настройте webhook

1. Скопируйте URL из Railway (например: `https://your-app.up.railway.app`)
2. Откройте [@BotFather](https://t.me/BotFather)
3. `/setwebhook` → `https://your-app.up.railway.app/webhook`

## 6. Готово! 🎉

Ваш бот работает на Railway!

---

📖 **Подробная инструкция**: [DEPLOYMENT.md](DEPLOYMENT.md)
