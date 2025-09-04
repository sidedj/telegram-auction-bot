# Файл: auction_persistence.py
import asyncio
import json
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class AuctionPersistence:
    """
    Класс для сохранения и восстановления состояния аукционов
    """
    
    def __init__(self, db, persistence_file: str = "auction_state.json"):
        self.db = db
        self.persistence_file = Path(persistence_file)
        self.running = False
        self.save_task = None
        
    async def start(self):
        """Запустить систему персистентности"""
        if self.running:
            return
            
        self.running = True
        
        # Восстанавливаем состояние при запуске
        await self.restore_state()
        
        # Запускаем периодическое сохранение
        self.save_task = asyncio.create_task(self._periodic_save())
        
        # Регистрируем обработчики сигналов
        self._register_signal_handlers()
        
        logging.info("Auction persistence system started")
    
    async def stop(self):
        """Остановить систему персистентности"""
        self.running = False
        
        if self.save_task:
            self.save_task.cancel()
            try:
                await self.save_task
            except asyncio.CancelledError:
                pass
        
        # Сохраняем состояние при остановке
        await self.save_state()
        
        logging.info("Auction persistence system stopped")
    
    def _register_signal_handlers(self):
        """Регистрируем обработчики сигналов для корректного завершения"""
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, saving state...")
            asyncio.create_task(self.save_state())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _periodic_save(self):
        """Периодическое сохранение состояния каждые 5 минут"""
        while self.running:
            try:
                await asyncio.sleep(300)  # 5 минут
                if self.running:
                    await self.save_state()
                    logging.debug("Periodic state save completed")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in periodic save: {e}")
    
    async def save_state(self):
        """Сохранить текущее состояние аукционов"""
        try:
            # Получаем все активные аукционы
            active_auctions = await self._get_active_auctions()
            
            # Получаем все ставки для активных аукционов
            auction_bids = {}
            for auction in active_auctions:
                auction_id = auction['id']
                bids = await self._get_auction_bids(auction_id)
                auction_bids[auction_id] = bids
            
            # Формируем данные для сохранения
            state_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'active_auctions': active_auctions,
                'auction_bids': auction_bids,
                'total_active_auctions': len(active_auctions)
            }
            
            # Сохраняем в файл
            with open(self.persistence_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2, default=str)
            
            logging.info(f"State saved: {len(active_auctions)} active auctions")
            return True
            
        except Exception as e:
            logging.error(f"Error saving state: {e}")
            return False
    
    async def restore_state(self):
        """Восстановить состояние аукционов из файла"""
        try:
            if not self.persistence_file.exists():
                logging.info("No persistence file found, starting fresh")
                return True
            
            # Читаем файл состояния
            with open(self.persistence_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Проверяем версию
            if state_data.get('version') != '1.0':
                logging.warning(f"Unknown persistence version: {state_data.get('version')}")
                return False
            
            # Восстанавливаем аукционы
            restored_count = 0
            active_auctions = state_data.get('active_auctions', [])
            
            for auction_data in active_auctions:
                try:
                    # Проверяем, что аукцион все еще активен по времени
                    end_time_str = auction_data.get('end_time')
                    if isinstance(end_time_str, str):
                        end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                    else:
                        end_time = datetime.now()
                    
                    # Если время истекло, пропускаем
                    if end_time <= datetime.now():
                        logging.info(f"Auction {auction_data.get('id')} expired, skipping restoration")
                        continue
                    
                    # Проверяем, существует ли аукцион в базе данных
                    existing_auction = await self.db.get_auction(auction_data.get('id'))
                    if existing_auction:
                        # Обновляем статус на активный, если он был изменен
                        if existing_auction['status'] != 'active':
                            await self.db.update_auction_status(auction_data.get('id'), 'active')
                            logging.info(f"Restored auction {auction_data.get('id')} status to active")
                        restored_count += 1
                    else:
                        logging.warning(f"Auction {auction_data.get('id')} not found in database")
                        
                except Exception as e:
                    logging.error(f"Error restoring auction {auction_data.get('id', 'unknown')}: {e}")
            
            # Восстанавливаем ставки
            auction_bids = state_data.get('auction_bids', {})
            restored_bids = 0
            
            for auction_id, bids in auction_bids.items():
                try:
                    # Проверяем, что аукцион существует
                    auction = await self.db.get_auction(int(auction_id))
                    if not auction:
                        continue
                    
                    # Восстанавливаем ставки (если они не существуют)
                    for bid in bids:
                        try:
                            # Проверяем, существует ли ставка
                            existing_bids = await self.db.get_bidding_history(int(auction_id))
                            bid_exists = any(
                                existing_bid['amount'] == bid['amount'] and 
                                existing_bid['bidder_id'] == bid['bidder_id'] and
                                existing_bid['created_at'] == bid['created_at']
                                for existing_bid in existing_bids
                            )
                            
                            if not bid_exists:
                                # Восстанавливаем ставку
                                await self.db.place_bid(
                                    int(auction_id),
                                    bid['bidder_id'],
                                    bid['bidder_username'],
                                    bid['amount']
                                )
                                restored_bids += 1
                                
                        except Exception as e:
                            logging.error(f"Error restoring bid for auction {auction_id}: {e}")
                            
                except Exception as e:
                    logging.error(f"Error restoring bids for auction {auction_id}: {e}")
            
            logging.info(f"State restored: {restored_count} auctions, {restored_bids} bids")
            return True
            
        except Exception as e:
            logging.error(f"Error restoring state: {e}")
            return False
    
    async def _get_active_auctions(self) -> List[Dict]:
        """Получить все активные аукционы"""
        try:
            import aiosqlite
            async with aiosqlite.connect(self.db.db_path) as db_conn:
                cursor = await db_conn.execute(
                    "SELECT * FROM auctions WHERE status = 'active' AND end_time > ?",
                    (datetime.now(),)
                )
                auctions = await cursor.fetchall()
                
                result = []
                for auction in auctions:
                    # Получаем медиа файлы
                    cursor = await db_conn.execute(
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
                            end_time = datetime.now()
                    
                    created_at = auction[12]
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except ValueError:
                            created_at = datetime.now()
                    
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
                
        except Exception as e:
            logging.error(f"Error getting active auctions: {e}")
            return []
    
    async def _get_auction_bids(self, auction_id: int) -> List[Dict]:
        """Получить все ставки для аукциона"""
        try:
            return await self.db.get_bidding_history(auction_id)
        except Exception as e:
            logging.error(f"Error getting bids for auction {auction_id}: {e}")
            return []
    
    async def force_save(self):
        """Принудительно сохранить состояние"""
        return await self.save_state()
    
    def get_persistence_info(self) -> Dict:
        """Получить информацию о файле персистентности"""
        try:
            if not self.persistence_file.exists():
                return {
                    'exists': False,
                    'size': 0,
                    'last_modified': None
                }
            
            stat = self.persistence_file.stat()
            return {
                'exists': True,
                'size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'path': str(self.persistence_file.absolute())
            }
        except Exception as e:
            logging.error(f"Error getting persistence info: {e}")
            return {'error': str(e)}
