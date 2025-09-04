# Файл: api_client.py
"""
Модуль для работы с внешними API
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import ipaddress

class APIClient:
    """Клиент для работы с внешними API"""
    
    def __init__(self, base_url: str, api_key: str = None, timeout: int = 30, allowed_ips: List[str] = None):
        """
        Инициализация API клиента
        
        Args:
            base_url: Базовый URL API
            api_key: API ключ (если требуется)
            timeout: Таймаут запросов в секундах
            allowed_ips: Список разрешенных IP-адресов
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.allowed_ips = allowed_ips or []
        self.session = None
        
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки для запросов"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'AuctionBot/1.0'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        return headers
    
    def _is_ip_allowed(self, ip: str) -> bool:
        """
        Проверить, разрешен ли IP-адрес
        
        Args:
            ip: IP-адрес для проверки
            
        Returns:
            True если IP разрешен, False иначе
        """
        if not self.allowed_ips:
            return True  # Если список пуст, разрешаем все IP
        
        try:
            # Парсим IP-адрес
            ip_obj = ipaddress.ip_address(ip)
            
            # Проверяем каждый разрешенный IP
            for allowed_ip in self.allowed_ips:
                try:
                    # Поддерживаем как отдельные IP, так и подсети
                    if '/' in allowed_ip:
                        # Это подсеть
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if ip_obj in network:
                            return True
                    else:
                        # Это отдельный IP
                        if str(ip_obj) == allowed_ip:
                            return True
                except ValueError:
                    # Неверный формат IP в списке разрешенных
                    logging.warning(f"Неверный формат IP в списке разрешенных: {allowed_ip}")
                    continue
            
            return False
            
        except ValueError:
            # Неверный формат IP
            logging.warning(f"Неверный формат IP: {ip}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """
        Выполнить HTTP запрос
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Конечная точка API
            data: Данные для отправки (для POST/PUT)
            params: Параметры запроса (для GET)
            
        Returns:
            Ответ API в виде словаря
            
        Raises:
            APIClientError: Ошибка при выполнении запроса
        """
        if not self.session:
            raise APIClientError("Сессия не инициализирована. Используйте async with")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            # Проверяем IP-адрес сервера (если настроены ограничения)
            if self.allowed_ips:
                try:
                    # Извлекаем IP из URL
                    from urllib.parse import urlparse
                    parsed_url = urlparse(url)
                    server_ip = parsed_url.hostname
                    
                    # Проверяем, разрешен ли IP
                    if not self._is_ip_allowed(server_ip):
                        raise APIClientError(f"IP-адрес {server_ip} не разрешен для доступа к API")
                        
                except Exception as e:
                    logging.warning(f"Не удалось проверить IP-адрес: {e}")
            
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            ) as response:
                
                # Логируем запрос
                logging.info(f"API Request: {method} {url}")
                logging.info(f"API Response Status: {response.status}")
                
                # Проверяем статус ответа
                if response.status >= 400:
                    error_text = await response.text()
                    logging.error(f"API Error {response.status}: {error_text}")
                    raise APIClientError(f"API Error {response.status}: {error_text}")
                
                # Парсим JSON ответ
                try:
                    result = await response.json()
                except json.JSONDecodeError:
                    text = await response.text()
                    logging.warning(f"API returned non-JSON response: {text}")
                    return {"raw_response": text}
                
                return result
                
        except aiohttp.ClientError as e:
            logging.error(f"API Client Error: {e}")
            raise APIClientError(f"Ошибка соединения с API: {e}")
        except asyncio.TimeoutError:
            logging.error(f"API Timeout: {self.timeout.total} seconds")
            raise APIClientError(f"Таймаут запроса: {self.timeout.total} секунд")
    
    async def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """GET запрос"""
        return await self._make_request('GET', endpoint, params=params)
    
    async def post(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """POST запрос"""
        return await self._make_request('POST', endpoint, data=data)
    
    async def put(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """PUT запрос"""
        return await self._make_request('PUT', endpoint, data=data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE запрос"""
        return await self._make_request('DELETE', endpoint)


class APIClientError(Exception):
    """Исключение для ошибок API клиента"""
    pass


class AuctionAPIClient(APIClient):
    """Специализированный клиент для работы с API аукционов"""
    
    def __init__(self, base_url: str, api_key: str = None, timeout: int = 30, allowed_ips: List[str] = None):
        super().__init__(base_url, api_key, timeout, allowed_ips)
    
    async def get_auction_stats(self) -> Dict[str, Any]:
        """Получить статистику аукционов"""
        return await self.get('/auctions/stats')
    
    async def create_auction(self, auction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать аукцион через API"""
        return await self.post('/auctions', data=auction_data)
    
    async def update_auction(self, auction_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить аукцион через API"""
        return await self.put(f'/auctions/{auction_id}', data=update_data)
    
    async def get_auction(self, auction_id: int) -> Dict[str, Any]:
        """Получить информацию об аукционе"""
        return await self.get(f'/auctions/{auction_id}')
    
    async def place_bid(self, auction_id: int, bid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Сделать ставку через API"""
        return await self.post(f'/auctions/{auction_id}/bids', data=bid_data)
    
    async def get_user_auctions(self, user_id: int) -> Dict[str, Any]:
        """Получить аукционы пользователя"""
        return await self.get(f'/users/{user_id}/auctions')
    
    async def get_auction_bids(self, auction_id: int) -> Dict[str, Any]:
        """Получить ставки по аукциону"""
        return await self.get(f'/auctions/{auction_id}/bids')


class NotificationAPIClient(APIClient):
    """Клиент для работы с API уведомлений"""
    
    def __init__(self, base_url: str, api_key: str = None, timeout: int = 30, allowed_ips: List[str] = None):
        super().__init__(base_url, api_key, timeout, allowed_ips)
    
    async def send_notification(self, user_id: int, message: str, notification_type: str = "info") -> Dict[str, Any]:
        """Отправить уведомление пользователю"""
        data = {
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now().isoformat()
        }
        return await self.post('/notifications', data=data)
    
    async def send_bulk_notifications(self, notifications: list) -> Dict[str, Any]:
        """Отправить массовые уведомления"""
        return await self.post('/notifications/bulk', data={"notifications": notifications})


class PaymentAPIClient(APIClient):
    """Клиент для работы с API платежей"""
    
    def __init__(self, base_url: str, api_key: str = None, timeout: int = 30, allowed_ips: List[str] = None):
        super().__init__(base_url, api_key, timeout, allowed_ips)
    
    async def create_payment(self, amount: int, currency: str, description: str, user_id: int) -> Dict[str, Any]:
        """Создать платеж"""
        data = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        return await self.post('/payments', data=data)
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Получить статус платежа"""
        return await self.get(f'/payments/{payment_id}/status')
    
    async def process_payment(self, payment_id: str) -> Dict[str, Any]:
        """Обработать платеж"""
        return await self.post(f'/payments/{payment_id}/process')


# Пример использования
async def example_usage():
    """Пример использования API клиентов"""
    
    # Настройки API (должны быть в config.py)
    API_BASE_URL = "https://api.example.com"
    API_KEY = "your_api_key_here"
    
    try:
        # Использование AuctionAPIClient
        async with AuctionAPIClient(API_BASE_URL, API_KEY) as auction_client:
            # Получить статистику
            stats = await auction_client.get_auction_stats()
            print(f"Статистика аукционов: {stats}")
            
            # Создать аукцион
            auction_data = {
                "description": "Тестовый товар",
                "start_price": 1000,
                "blitz_price": 5000,
                "duration_hours": 24,
                "owner_id": 123456789
            }
            result = await auction_client.create_auction(auction_data)
            print(f"Аукцион создан: {result}")
    
    except APIClientError as e:
        logging.error(f"Ошибка API: {e}")
    except Exception as e:
        logging.error(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    # Запуск примера
    asyncio.run(example_usage())
