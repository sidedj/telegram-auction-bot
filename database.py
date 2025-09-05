# Файл: database.py
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

try:
    import aiosqlite
except ImportError:
    print("aiosqlite не установлен. Установите: pip install aiosqlite")
    raise

class Database:
    def __init__(self, db_path: str = "auction_bot.db"):
        self.db_path = db_path
        
    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    balance INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Таблица аукционов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS auctions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    start_price INTEGER NOT NULL,
                    blitz_price INTEGER,
                    current_price INTEGER NOT NULL,
                    current_leader_id INTEGER,
                    current_leader_username TEXT,
                    end_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'active', -- active, sold, expired
                    channel_message_id INTEGER,
                    channel_chat_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица медиа файлов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS auction_media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auction_id INTEGER NOT NULL,
                    file_id TEXT NOT NULL,
                    media_type TEXT NOT NULL, -- photo, video
                    order_index INTEGER NOT NULL,
                    FOREIGN KEY (auction_id) REFERENCES auctions (id) ON DELETE CASCADE
                )
            """)
            
            # Таблица ставок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bids (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auction_id INTEGER NOT NULL,
                    bidder_id INTEGER NOT NULL,
                    bidder_username TEXT,
                    amount INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (auction_id) REFERENCES auctions (id) ON DELETE CASCADE,
                    FOREIGN KEY (bidder_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица транзакций (для истории пополнений)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL, -- purchase, admin_grant, auction_created
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            await db.commit()
            logging.info("Database initialized successfully")

    async def get_or_create_user(self, user_id: int, username: str = None, full_name: str = None) -> Dict:
        """Получить или создать пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем существование пользователя
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            user = await cursor.fetchone()
            
            if user:
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'full_name': user[2],
                    'balance': user[3],
                    'created_at': user[4],
                    'is_admin': bool(user[5]),
                    'is_new_user': False  # Пользователь уже существовал
                }
            else:
                # Создаем нового пользователя
                await db.execute(
                    "INSERT INTO users (user_id, username, full_name, balance) VALUES (?, ?, ?, ?)",
                    (user_id, username, full_name, 0)
                )
                await db.commit()
                
                return {
                    'user_id': user_id,
                    'username': username,
                    'full_name': full_name,
                    'balance': 0,
                    'created_at': datetime.now(),
                    'is_admin': False,
                    'is_new_user': True  # Пользователь только что создан
                }

    async def update_user_balance(self, user_id: int, amount: int, transaction_type: str, description: str = None) -> bool:
        """Обновить баланс пользователя и записать транзакцию"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, существует ли пользователь
                cursor = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                if not await cursor.fetchone():
                    # Создаем пользователя, если его нет
                    await db.execute(
                        "INSERT INTO users (user_id, username, full_name, balance, is_admin) VALUES (?, ?, ?, ?, ?)",
                        (user_id, None, None, 0, False)
                    )
                
                # Обновляем баланс
                await db.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                    (amount, user_id)
                )
                
                # Записываем транзакцию
                await db.execute(
                    "INSERT INTO transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)",
                    (user_id, amount, transaction_type, description)
                )
                
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Error updating user balance: {e}")
            return False

    async def create_auction(self, owner_id: int, description: str, start_price: int, 
                           blitz_price: int, end_time: datetime, media_files: List[Dict]) -> int:
        """Создать новый аукцион"""
        async with aiosqlite.connect(self.db_path) as db:
            # Создаем аукцион
            cursor = await db.execute(
                """INSERT INTO auctions (owner_id, description, start_price, blitz_price, 
                   current_price, end_time) VALUES (?, ?, ?, ?, ?, ?)""",
                (owner_id, description, start_price, blitz_price, start_price, end_time)
            )
            auction_id = cursor.lastrowid
            
            # Добавляем медиа файлы
            for i, media in enumerate(media_files):
                await db.execute(
                    "INSERT INTO auction_media (auction_id, file_id, media_type, order_index) VALUES (?, ?, ?, ?)",
                    (auction_id, media['file_id'], media['type'], i)
                )
            
            await db.commit()
            return auction_id

    async def get_auction(self, auction_id: int) -> Optional[Dict]:
        """Получить аукцион по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM auctions WHERE id = ?", (auction_id,)
            )
            auction = await cursor.fetchone()
            
            if not auction:
                return None
                
            # Получаем медиа файлы
            cursor = await db.execute(
                "SELECT file_id, media_type, order_index FROM auction_media WHERE auction_id = ? ORDER BY order_index",
                (auction_id,)
            )
            media = await cursor.fetchall()
            
            # Преобразуем строки дат в datetime объекты
            end_time = auction[8]
            if isinstance(end_time, str):
                try:
                    end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                except ValueError:
                    end_time = datetime.now()  # Fallback
            
            created_at = auction[12]
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except ValueError:
                    created_at = datetime.now()  # Fallback
            
            return {
                'id': auction[0],
                'owner_id': auction[1],
                'description': auction[2],
                'start_price': auction[3],
                'blitz_price': auction[4],
                'current_price': auction[5],
                'current_leader_id': auction[6],
                'current_leader_username': auction[7],
                'end_time': end_time,
                'status': auction[9],
                'channel_message_id': auction[10],
                'channel_chat_id': auction[11],
                'created_at': created_at,
                'media': [{'file_id': m[0], 'type': m[1]} for m in media]
            }

    async def get_user_auctions(self, user_id: int, status: str = None) -> List[Dict]:
        """Получить аукционы пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            if status == 'active':
                # Для активных аукционов дополнительно проверяем, что время не истекло
                cursor = await db.execute(
                    "SELECT * FROM auctions WHERE owner_id = ? AND status = ? AND end_time > ? ORDER BY created_at DESC",
                    (user_id, status, datetime.now())
                )
            elif status:
                cursor = await db.execute(
                    "SELECT * FROM auctions WHERE owner_id = ? AND status = ? ORDER BY created_at DESC",
                    (user_id, status)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM auctions WHERE owner_id = ? ORDER BY created_at DESC",
                    (user_id,)
                )
            
            auctions = await cursor.fetchall()
            result = []
            
            for auction in auctions:
                # Получаем медиа для каждого аукциона
                cursor = await db.execute(
                    "SELECT file_id, media_type, order_index FROM auction_media WHERE auction_id = ? ORDER BY order_index",
                    (auction[0],)
                )
                media = await cursor.fetchall()
                
                # Преобразуем строки дат в datetime объекты
                end_time = auction[8]
                if isinstance(end_time, str):
                    try:
                        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    except ValueError:
                        end_time = datetime.now()  # Fallback
                
                created_at = auction[12]
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except ValueError:
                        created_at = datetime.now()  # Fallback
                
                result.append({
                    'id': auction[0],
                    'owner_id': auction[1],
                    'description': auction[2],
                    'start_price': auction[3],
                    'blitz_price': auction[4],
                    'current_price': auction[5],
                    'current_leader_id': auction[6],
                    'current_leader_username': auction[7],
                    'end_time': end_time,
                    'status': auction[9],
                    'channel_message_id': auction[10],
                    'channel_chat_id': auction[11],
                    'created_at': created_at,
                    'media': [{'file_id': m[0], 'type': m[1]} for m in media]
                })
            
            return result

    async def get_truly_active_auctions_count(self, user_id: int = None) -> int:
        """Получить количество действительно активных аукционов (не истекших по времени)"""
        async with aiosqlite.connect(self.db_path) as db:
            if user_id:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM auctions WHERE owner_id = ? AND status = 'active' AND end_time > ?",
                    (user_id, datetime.now())
                )
            else:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM auctions WHERE status = 'active' AND end_time > ?",
                    (datetime.now(),)
                )
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def update_auction_status(self, auction_id: int, status: str):
        """Обновить статус аукциона"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE auctions SET status = ? WHERE id = ?",
                (status, auction_id)
            )
            await db.commit()

    async def place_bid(self, auction_id: int, bidder_id: int, bidder_username: str, amount: int) -> bool:
        """Сделать ставку"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, что аукцион активен
            cursor = await db.execute(
                "SELECT status, current_price, blitz_price FROM auctions WHERE id = ?",
                (auction_id,)
            )
            auction = await cursor.fetchone()
            
            if not auction or auction[0] != 'active':
                return False
                
            current_price = auction[1]
            blitz_price = auction[2]
            
            # Проверяем, что ставка больше текущей
            if amount <= current_price:
                return False
                
            # Проверяем, что не превышаем блиц-цену
            if blitz_price and amount >= blitz_price:
                amount = blitz_price
            
            # Обновляем аукцион
            await db.execute(
                """UPDATE auctions SET current_price = ?, current_leader_id = ?, 
                   current_leader_username = ? WHERE id = ?""",
                (amount, bidder_id, bidder_username, auction_id)
            )
            
            # Записываем ставку
            await db.execute(
                "INSERT INTO bids (auction_id, bidder_id, bidder_username, amount) VALUES (?, ?, ?, ?)",
                (auction_id, bidder_id, bidder_username, amount)
            )
            
            await db.commit()
            return True

    async def get_expired_auctions(self) -> List[Dict]:
        """Получить истекшие аукционы"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM auctions WHERE status = 'active' AND end_time < ?",
                (datetime.now(),)
            )
            auctions = await cursor.fetchall()
            
            result = []
            for auction in auctions:
                # Преобразуем строку даты в datetime объект
                end_time = auction[8]
                if isinstance(end_time, str):
                    try:
                        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    except ValueError:
                        end_time = datetime.now()  # Fallback
                
                created_at = auction[12]
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except ValueError:
                        created_at = datetime.now()  # Fallback
                
                result.append({
                    'id': auction[0],
                    'owner_id': auction[1],
                    'description': auction[2],
                    'start_price': auction[3],
                    'blitz_price': auction[4],
                    'current_price': auction[5],
                    'current_leader_id': auction[6],
                    'current_leader_username': auction[7],
                    'end_time': end_time,
                    'status': auction[9],
                    'channel_message_id': auction[10],
                    'channel_chat_id': auction[11],
                    'created_at': created_at
                })
            
            return result

    async def set_auction_channel_info(self, auction_id: int, channel_chat_id: int, channel_message_id: int):
        """Установить информацию о сообщении в канале"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE auctions SET channel_chat_id = ?, channel_message_id = ? WHERE id = ?",
                (channel_chat_id, channel_message_id, auction_id)
            )
            await db.commit()

    async def get_auction_by_channel_message(self, chat_id: int, message_id: int) -> Optional[Dict]:
        """Получить аукцион по сообщению в канале"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM auctions WHERE channel_chat_id = ? AND channel_message_id = ?",
                (chat_id, message_id)
            )
            auction = await cursor.fetchone()
            
            if not auction:
                return None
                
            # Преобразуем строки дат в datetime объекты
            end_time = auction[8]
            if isinstance(end_time, str):
                try:
                    end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                except ValueError:
                    end_time = datetime.now()  # Fallback
            
            created_at = auction[12]
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except ValueError:
                    created_at = datetime.now()  # Fallback
            
            return {
                'id': auction[0],
                'owner_id': auction[1],
                'description': auction[2],
                'start_price': auction[3],
                'blitz_price': auction[4],
                'current_price': auction[5],
                'current_leader_id': auction[6],
                'current_leader_username': auction[7],
                'end_time': end_time,
                'status': auction[9],
                'channel_message_id': auction[10],
                'channel_chat_id': auction[11],
                'created_at': created_at
            }

    async def get_bidding_history(self, auction_id: int) -> List[Dict]:
        """Получить историю ставок для аукциона"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT bidder_id, bidder_username, amount, created_at FROM bids 
                   WHERE auction_id = ? ORDER BY created_at DESC""",
                (auction_id,)
            )
            bids = await cursor.fetchall()
            
            return [
                {
                    'bidder_id': bid[0],
                    'bidder_username': bid[1],
                    'amount': bid[2],
                    'created_at': bid[3]
                }
                for bid in bids
            ]

    async def grant_admin_status(self, user_id: int):
        """Выдать права администратора"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_admin = TRUE WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()

    async def get_user_balance(self, user_id: int) -> int:
        """Получить баланс пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT balance FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def has_recent_payment(self, user_id: int, minutes: int = 10) -> bool:
        """Проверить, был ли недавний платеж пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT COUNT(*) FROM transactions 
                   WHERE user_id = ? AND transaction_type = 'purchase' 
                   AND created_at > datetime('now', '-{} minutes')""".format(minutes),
                (user_id,)
            )
            result = await cursor.fetchone()
            count = result[0] if result else 0
            logging.info(f"Проверка недавних платежей для пользователя {user_id}: найдено {count} транзакций за последние {minutes} минут")
            return count > 0
