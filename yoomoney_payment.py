# Файл: yoomoney_payment.py

import urllib.parse
import logging
from typing import Dict, Optional
from config import YOOMONEY_RECEIVER, YOOMONEY_BASE_URL, PAYMENT_PLANS

logger = logging.getLogger(__name__)

class YooMoneyPayment:
    """Класс для работы с платежами через ЮMoney"""
    
    def __init__(self):
        self.receiver = YOOMONEY_RECEIVER
        self.base_url = YOOMONEY_BASE_URL
    
    def generate_payment_url(self, plan_id: str, user_id: int) -> Optional[str]:
        """
        Генерирует уникальную ссылку на оплату для пользователя
        
        Args:
            plan_id: ID тарифного плана (1, 5, 10, 20)
            user_id: Telegram ID пользователя
            
        Returns:
            str: URL для оплаты или None при ошибке
        """
        try:
            if plan_id not in PAYMENT_PLANS:
                logger.error(f"Неизвестный план оплаты: {plan_id}")
                return None
            
            plan = PAYMENT_PLANS[plan_id]
            price = plan["price"]
            description = plan["description"]
            
            # Создаем уникальный label для пользователя
            label = f"user_{user_id}"
            
            # Параметры для URL
            params = {
                "receiver": self.receiver,
                "quickpay-form": "shop",
                "targets": description,
                "paymentType": "AC",
                "sum": str(price),
                "label": label
            }
            
            # Кодируем параметры в URL
            query_string = urllib.parse.urlencode(params)
            payment_url = f"{self.base_url}?{query_string}"
            
            logger.info(f"Сгенерирована ссылка на оплату для пользователя {user_id}, план {plan_id}")
            return payment_url
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ссылки на оплату: {e}")
            return None
    
    def get_payment_plans(self) -> Dict[str, Dict]:
        """
        Возвращает доступные тарифные планы
        
        Returns:
            Dict: Словарь с тарифными планами
        """
        return PAYMENT_PLANS.copy()
    
    def validate_payment_data(self, notification_data: Dict) -> tuple[bool, str]:
        """
        Валидирует данные уведомления от ЮMoney
        
        Args:
            notification_data: Данные уведомления
            
        Returns:
            tuple: (валидность, сообщение об ошибке)
        """
        required_fields = ["notification_secret", "label", "amount", "operation_id", "unaccepted"]
        
        for field in required_fields:
            if field not in notification_data:
                return False, f"Отсутствует обязательное поле: {field}"
        
        # Проверяем, что это не отклоненная операция
        if notification_data.get("unaccepted") != "false":
            return False, "Операция не подтверждена"
        
        # Проверяем формат label
        label = notification_data.get("label", "")
        if not label.startswith("user_"):
            return False, "Неверный формат label"
        
        try:
            user_id = int(label.replace("user_", ""))
            if user_id <= 0:
                return False, "Неверный ID пользователя"
        except ValueError:
            return False, "Неверный формат ID пользователя в label"
        
        return True, "OK"
    
    def extract_user_id_from_label(self, label: str) -> Optional[int]:
        """
        Извлекает ID пользователя из label
        
        Args:
            label: Label из уведомления
            
        Returns:
            int: ID пользователя или None при ошибке
        """
        try:
            if label.startswith("user_"):
                return int(label.replace("user_", ""))
            return None
        except ValueError:
            return None
