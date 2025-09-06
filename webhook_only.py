#!/usr/bin/env python3
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/yoomoney', methods=['POST', 'GET'])
def yoomoney_webhook():
    """Простой webhook для YooMoney"""
    try:
        print("=" * 50)
        print("ПОЛУЧЕН ЗАПРОС")
        print(f"Метод: {request.method}")
        print(f"URL: {request.url}")
        print(f"IP: {request.remote_addr}")
        
        if request.method == 'GET':
            return {"status": "ok", "message": "Webhook ready"}
        
        # Получаем данные
        form_data = request.form.to_dict()
        print(f"Данные формы: {form_data}")
        
        # Простая обработка
        amount = form_data.get('amount', '0')
        is_test = form_data.get('test_notification') == 'true'
        
        print(f"Сумма: {amount}")
        print(f"Тестовое: {is_test}")
        
        if is_test:
            print("✅ ТЕСТОВОЕ УВЕДОМЛЕНИЕ ОБРАБОТАНО УСПЕШНО!")
            return "ok", 200
        else:
            print("✅ РЕАЛЬНЫЙ ПЛАТЕЖ ОБРАБОТАН УСПЕШНО!")
            return "ok", 200
            
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return "error", 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return {"status": "ok", "message": "Webhook service is running"}

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
