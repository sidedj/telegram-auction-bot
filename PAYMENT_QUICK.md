# ⚡ Быстрая настройка платежей

## 🎯 Что нужно сделать

### 1. Получить номер кошелька ЮMoney
1. Зайдите на [yoomoney.ru](https://yoomoney.ru)
2. Создайте кошелек
3. Скопируйте номер (например: `4100118987681575`)

### 2. Настроить webhook в ЮMoney
1. Войдите в [личный кабинет ЮMoney](https://yoomoney.ru)
2. **Настройки** → **HTTP-уведомления**
3. **Подключить уведомления**
4. Заполните:
   - **URL**: `https://ваш-проект.up.railway.app/yoomoney`
   - **Секрет**: `SaTKEuJWPVXJI/JFpXDCHZ4q`
5. **Подключить**

### 3. Добавить переменные в Railway
В Railway Dashboard → Variables:

```env
YOOMONEY_RECEIVER=ваш_номер_кошелька
YOOMONEY_SECRET=SaTKEuJWPVXJI/JFpXDCHZ4q
YOOMONEY_NOTIFICATION_URL=https://ваш-проект.up.railway.app/yoomoney
```

### 4. Готово! 🎉
Платежи работают автоматически!

---

📖 **Подробная инструкция**: [PAYMENT_SETUP.md](PAYMENT_SETUP.md)
