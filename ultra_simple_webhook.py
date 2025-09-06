#!/usr/bin/env python3
from flask import Flask, request
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/yoomoney', methods=['POST', 'GET'])
def yoomoney_webhook():
    """УЛЬТРА ПРОСТОЙ webhook для тестирования"""
    try:
        logger.info("=" * 50)
        logger.info("ПОЛУЧЕН ЗАПРОС")
        logger.info(f"Метод: {request.method}")
        logger.info(f"URL: {request.url}")
        logger.info(f"IP: {request.remote_addr}")
        
        if request.method == 'GET':
            return {"status": "ok", "message": "Webhook ready"}
        
        # Получаем данные
        form_data = request.form.to_dict()
        logger.info(f"Данные формы: {form_data}")
        
        # Простая обработка
        amount = form_data.get('amount', '0')
        is_test = form_data.get('test_notification') == 'true'
        
        logger.info(f"Сумма: {amount}")
        logger.info(f"Тестовое: {is_test}")
        
        if is_test:
            logger.info("✅ ТЕСТОВОЕ УВЕДОМЛЕНИЕ ОБРАБОТАНО УСПЕШНО!")
            return "ok", 200
        else:
            logger.info("✅ РЕАЛЬНЫЙ ПЛАТЕЖ ОБРАБОТАН УСПЕШНО!")
            return "ok", 200
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "error", 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return {"status": "ok", "message": "Service is running"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
