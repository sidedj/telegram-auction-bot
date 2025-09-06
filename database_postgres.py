# Файл: database_postgres.py
import asyncio
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

try:
    import asyncpg
except ImportError:
    print("asyncpg не установлен. Установите: pip install asyncpg")
    raise

class Database:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL не установлен")
        
    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        conn = await asyncpg.connect(self.database_url)
        try:
            # Таблица пользователей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    balance INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Таблица аукционов
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS auctions (
                    id SERIAL PRIMARY KEY,
                    owner_id BIGINT NOT NULL,
                    description TEXT NOT NULL,
                    start_price INTEGER NOT NULL,
                    blitz_price INTEGER,
                    current_price INTEGER NOT NULL,
                    current_leader_id BIGINT,
                    current_leader_username TEXT,
                    end_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'active',
                    channel_message_id BIGINT,
                    channel_chat_id BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица ставок
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bids (
                    id SERIAL PRIMARY KEY,
                    auction_id INTEGER NOT NULL,
                    bidder_id BIGINT NOT NULL,
                    bidder_username TEXT,
                    amount INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (auction_id) REFERENCES auctions (id),
                    FOREIGN KEY (bidder_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица транзакций
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    amount INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица обработанных платежей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_payments (
                    operation_id TEXT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    publications INTEGER NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            logging.info("Database tables created successfully")
            
        finally:
            await conn.close()

    async def get_or_create_user(self, user_id: int, username: str = None, full_name: str = None) -> Dict:
        """Получает или создает пользователя"""
        conn = await asyncpg.connect(self.database_url)
        try:
            # Пытаемся получить существующего пользователя
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1", user_id
            )
            
            if row:
                return dict(row)
            
            # Создаем нового пользователя
            await conn.execute("""
                INSERT INTO users (user_id, username, full_name)
                VALUES ($1, $2, $3)
            """, user_id, username, full_name)
            
            # Возвращаем созданного пользователя
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1", user_id
            )
            return dict(row)
            
        finally:
            await conn.close()

    async def update_user_balance(self, user_id: int, new_balance: int) -> bool:
        """Обновляет баланс пользователя"""
        conn = await asyncpg.connect(self.database_url)
        try:
            await conn.execute(
                "UPDATE users SET balance = $1 WHERE user_id = $2",
                new_balance, user_id
            )
            return True
        except Exception as e:
            logging.error(f"Error updating user balance: {e}")
            return False
        finally:
            await conn.close()

    async def add_transaction(self, user_id: int, amount: int, transaction_type: str, description: str = None) -> bool:
        """Добавляет транзакцию"""
        conn = await asyncpg.connect(self.database_url)
        try:
            await conn.execute("""
                INSERT INTO transactions (user_id, amount, transaction_type, description)
                VALUES ($1, $2, $3, $4)
            """, user_id, amount, transaction_type, description)
            return True
        except Exception as e:
            logging.error(f"Error adding transaction: {e}")
            return False
        finally:
            await conn.close()

    async def has_recent_payment(self, user_id: int, minutes: int = 10) -> bool:
        """Проверяет, был ли недавний платеж"""
        conn = await asyncpg.connect(self.database_url)
        try:
            row = await conn.fetchrow("""
                SELECT 1 FROM processed_payments 
                WHERE user_id = $1 
                AND processed_at > NOW() - INTERVAL '%s minutes'
                LIMIT 1
            """ % minutes, user_id)
            return row is not None
        except Exception as e:
            logging.error(f"Error checking recent payment: {e}")
            return False
        finally:
            await conn.close()

    async def mark_payment_processed(self, operation_id: str, user_id: int, amount: float, publications: int) -> bool:
        """Отмечает платеж как обработанный"""
        conn = await asyncpg.connect(self.database_url)
        try:
            await conn.execute("""
                INSERT INTO processed_payments (operation_id, user_id, amount, publications)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (operation_id) DO NOTHING
            """, operation_id, user_id, amount, publications)
            return True
        except Exception as e:
            logging.error(f"Error marking payment as processed: {e}")
            return False
        finally:
            await conn.close()

    async def grant_admin_status(self, user_id: int) -> bool:
        """Предоставляет админский статус пользователю"""
        conn = await asyncpg.connect(self.database_url)
        try:
            await conn.execute(
                "UPDATE users SET is_admin = TRUE WHERE user_id = $1",
                user_id
            )
            return True
        except Exception as e:
            logging.error(f"Error granting admin status: {e}")
            return False
        finally:
            await conn.close()

    # Остальные методы для аукционов, ставок и т.д. можно добавить по необходимости
    async def create_auction(self, owner_id: int, description: str, start_price: int, 
                           blitz_price: int, end_time: datetime) -> int:
        """Создает новый аукцион"""
        conn = await asyncpg.connect(self.database_url)
        try:
            result = await conn.fetchval("""
                INSERT INTO auctions (owner_id, description, start_price, blitz_price, 
                                   current_price, end_time)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, owner_id, description, start_price, blitz_price, start_price, end_time)
            return result
        finally:
            await conn.close()

    async def get_auction(self, auction_id: int) -> Optional[Dict]:
        """Получает аукцион по ID"""
        conn = await asyncpg.connect(self.database_url)
        try:
            row = await conn.fetchrow(
                "SELECT * FROM auctions WHERE id = $1", auction_id
            )
            return dict(row) if row else None
        finally:
            await conn.close()

    async def get_active_auctions(self) -> List[Dict]:
        """Получает все активные аукционы"""
        conn = await asyncpg.connect(self.database_url)
        try:
            rows = await conn.fetch(
                "SELECT * FROM auctions WHERE status = 'active' ORDER BY created_at DESC"
            )
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def place_bid(self, auction_id: int, bidder_id: int, bidder_username: str, amount: int) -> bool:
        """Размещает ставку"""
        conn = await asyncpg.connect(self.database_url)
        try:
            async with conn.transaction():
                # Обновляем аукцион
                await conn.execute("""
                    UPDATE auctions 
                    SET current_price = $1, current_leader_id = $2, current_leader_username = $3
                    WHERE id = $4
                """, amount, bidder_id, bidder_username, auction_id)
                
                # Добавляем ставку
                await conn.execute("""
                    INSERT INTO bids (auction_id, bidder_id, bidder_username, amount)
                    VALUES ($1, $2, $3, $4)
                """, auction_id, bidder_id, bidder_username, amount)
                
            return True
        except Exception as e:
            logging.error(f"Error placing bid: {e}")
            return False
        finally:
            await conn.close()

    async def get_auction_bids(self, auction_id: int) -> List[Dict]:
        """Получает все ставки по аукциону"""
        conn = await asyncpg.connect(self.database_url)
        try:
            rows = await conn.fetch(
                "SELECT * FROM bids WHERE auction_id = $1 ORDER BY created_at DESC",
                auction_id
            )
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def update_auction_status(self, auction_id: int, status: str) -> bool:
        """Обновляет статус аукциона"""
        conn = await asyncpg.connect(self.database_url)
        try:
            await conn.execute(
                "UPDATE auctions SET status = $1 WHERE id = $2",
                status, auction_id
            )
            return True
        except Exception as e:
            logging.error(f"Error updating auction status: {e}")
            return False
        finally:
            await conn.close()

    async def get_user_auctions(self, user_id: int) -> List[Dict]:
        """Получает аукционы пользователя"""
        conn = await asyncpg.connect(self.database_url)
        try:
            rows = await conn.fetch(
                "SELECT * FROM auctions WHERE owner_id = $1 ORDER BY created_at DESC",
                user_id
            )
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def get_user_bids(self, user_id: int) -> List[Dict]:
        """Получает ставки пользователя"""
        conn = await asyncpg.connect(self.database_url)
        try:
            rows = await conn.fetch("""
                SELECT b.*, a.description as auction_description
                FROM bids b
                JOIN auctions a ON b.auction_id = a.id
                WHERE b.bidder_id = $1
                ORDER BY b.created_at DESC
            """, user_id)
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def get_user_transactions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Получает транзакции пользователя"""
        conn = await asyncpg.connect(self.database_url)
        try:
            rows = await conn.fetch(
                "SELECT * FROM transactions WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2",
                user_id, limit
            )
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def close(self):
        """Закрывает соединение с базой данных"""
        pass  # asyncpg не требует явного закрытия соединения
