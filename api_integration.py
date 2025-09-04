# Файл: api_integration.py
"""
Интеграция с внешними API для бота аукционов
"""

import logging
from typing import Dict, Any, Optional
from api_client import AuctionAPIClient, NotificationAPIClient, PaymentAPIClient, APIClientError
from config import EXTERNAL_API_URL, EXTERNAL_API_KEY, EXTERNAL_API_TIMEOUT, API_ALLOWED_IPS

class APIIntegration:
    """Класс для интеграции с внешними API"""
    
    def __init__(self):
        self.api_url = EXTERNAL_API_URL
        self.api_key = EXTERNAL_API_KEY
        self.timeout = EXTERNAL_API_TIMEOUT
        self.allowed_ips = API_ALLOWED_IPS
        self.enabled = bool(self.api_url and self.api_key)
        
        if not self.enabled:
            logging.warning("API интеграция отключена: не настроены URL или ключ API")
        elif self.allowed_ips:
            logging.info(f"API ограничен IP-адресами: {', '.join(self.allowed_ips)}")
    
    async def sync_auction_to_external(self, auction_data: Dict[str, Any]) -> bool:
        """
        Синхронизировать аукцион с внешним API
        
        Args:
            auction_data: Данные аукциона
            
        Returns:
            True если синхронизация успешна, False иначе
        """
        if not self.enabled:
            return False
        
        try:
            async with AuctionAPIClient(self.api_url, self.api_key, self.timeout, self.allowed_ips) as client:
                result = await client.create_auction(auction_data)
                logging.info(f"Аукцион синхронизирован с внешним API: {result}")
                return True
                
        except APIClientError as e:
            logging.error(f"Ошибка синхронизации аукциона: {e}")
            return False
        except Exception as e:
            logging.error(f"Неожиданная ошибка при синхронизации: {e}")
            return False
    
    async def sync_bid_to_external(self, auction_id: int, bid_data: Dict[str, Any]) -> bool:
        """
        Синхронизировать ставку с внешним API
        
        Args:
            auction_id: ID аукциона
            bid_data: Данные ставки
            
        Returns:
            True если синхронизация успешна, False иначе
        """
        if not self.enabled:
            return False
        
        try:
            async with AuctionAPIClient(self.api_url, self.api_key, self.timeout, self.allowed_ips) as client:
                result = await client.place_bid(auction_id, bid_data)
                logging.info(f"Ставка синхронизирована с внешним API: {result}")
                return True
                
        except APIClientError as e:
            logging.error(f"Ошибка синхронизации ставки: {e}")
            return False
        except Exception as e:
            logging.error(f"Неожиданная ошибка при синхронизации ставки: {e}")
            return False
    
    async def send_external_notification(self, user_id: int, message: str, notification_type: str = "info") -> bool:
        """
        Отправить уведомление через внешний API
        
        Args:
            user_id: ID пользователя
            message: Текст уведомления
            notification_type: Тип уведомления
            
        Returns:
            True если отправка успешна, False иначе
        """
        if not self.enabled:
            return False
        
        try:
            async with NotificationAPIClient(self.api_url, self.api_key, self.timeout, self.allowed_ips) as client:
                result = await client.send_notification(user_id, message, notification_type)
                logging.info(f"Уведомление отправлено через внешний API: {result}")
                return True
                
        except APIClientError as e:
            logging.error(f"Ошибка отправки уведомления: {e}")
            return False
        except Exception as e:
            logging.error(f"Неожиданная ошибка при отправке уведомления: {e}")
            return False
    
    async def process_external_payment(self, amount: int, currency: str, description: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Обработать платеж через внешний API
        
        Args:
            amount: Сумма платежа
            currency: Валюта
            description: Описание платежа
            user_id: ID пользователя
            
        Returns:
            Данные платежа или None при ошибке
        """
        if not self.enabled:
            return None
        
        try:
            async with PaymentAPIClient(self.api_url, self.api_key, self.timeout, self.allowed_ips) as client:
                result = await client.create_payment(amount, currency, description, user_id)
                logging.info(f"Платеж обработан через внешний API: {result}")
                return result
                
        except APIClientError as e:
            logging.error(f"Ошибка обработки платежа: {e}")
            return None
        except Exception as e:
            logging.error(f"Неожиданная ошибка при обработке платежа: {e}")
            return None
    
    async def get_external_auction_stats(self) -> Optional[Dict[str, Any]]:
        """
        Получить статистику аукционов с внешнего API
        
        Returns:
            Статистика или None при ошибке
        """
        if not self.enabled:
            return None
        
        try:
            async with AuctionAPIClient(self.api_url, self.api_key, self.timeout, self.allowed_ips) as client:
                result = await client.get_auction_stats()
                logging.info(f"Статистика получена с внешнего API: {result}")
                return result
                
        except APIClientError as e:
            logging.error(f"Ошибка получения статистики: {e}")
            return None
        except Exception as e:
            logging.error(f"Неожиданная ошибка при получении статистики: {e}")
            return None
    
    async def health_check(self) -> bool:
        """
        Проверить доступность внешнего API
        
        Returns:
            True если API доступен, False иначе
        """
        if not self.enabled:
            return False
        
        try:
            async with AuctionAPIClient(self.api_url, self.api_key, self.timeout, self.allowed_ips) as client:
                # Простой запрос для проверки доступности
                await client.get('/health')
                return True
                
        except Exception as e:
            logging.error(f"API недоступен: {e}")
            return False


# Глобальный экземпляр для использования в боте
api_integration = APIIntegration()


# Пример использования в боте
async def example_integration():
    """Пример интеграции с внешним API"""
    
    # Проверяем доступность API
    if await api_integration.health_check():
        print("✅ Внешний API доступен")
        
        # Получаем статистику
        stats = await api_integration.get_external_auction_stats()
        if stats:
            print(f"📊 Статистика: {stats}")
        
        # Отправляем уведомление
        success = await api_integration.send_external_notification(
            user_id=123456789,
            message="Тестовое уведомление",
            notification_type="info"
        )
        
        if success:
            print("✅ Уведомление отправлено")
        else:
            print("❌ Ошибка отправки уведомления")
    else:
        print("❌ Внешний API недоступен")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_integration())
