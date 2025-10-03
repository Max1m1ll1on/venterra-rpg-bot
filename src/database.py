# src/database.py - Робота з базою даних

import aiosqlite
import json
import logging
from typing import Optional, Dict, Any

from src.config.settings import settings

logger = logging.getLogger(__name__)


class Database:
    """Клас для роботи з базою даних"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
    
    async def init_db(self):
        """Ініціалізація бази даних - створення таблиць"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Включаємо підтримку зовнішніх ключів
                await db.execute("PRAGMA foreign_keys = ON")
                
                # Таблиця гравців
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS players (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        character_name TEXT DEFAULT 'Безіменний',
                        class TEXT DEFAULT 'warrior',
                        level INTEGER DEFAULT 1,
                        experience INTEGER DEFAULT 0,
                        gold INTEGER DEFAULT 100,
                        
                        strength INTEGER DEFAULT 0,
                        agility INTEGER DEFAULT 0,
                        intelligence INTEGER DEFAULT 0,
                        stamina INTEGER DEFAULT 0,
                        charisma INTEGER DEFAULT 0,
                        free_points INTEGER DEFAULT 5,
                        
                        health INTEGER DEFAULT 0,
                        max_health INTEGER DEFAULT 0,
                        
                        equipment TEXT DEFAULT '{}',
                        inventory TEXT DEFAULT '[]',
                        
                        current_location TEXT DEFAULT 'city',
                        
                        quests TEXT DEFAULT '{}',
                        achievements TEXT DEFAULT '[]',
                        last_daily_reward TEXT,
                        
                        monsters_killed INTEGER DEFAULT 0,
                        quests_completed INTEGER DEFAULT 0,
                        total_gold_earned INTEGER DEFAULT 100,
                        total_damage_dealt INTEGER DEFAULT 0,
                        total_damage_taken INTEGER DEFAULT 0,
                        
                        active_effects TEXT DEFAULT '[]',
                        
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                await db.commit()
                logger.info("База даних успішно ініціалізована")
                
        except Exception as e:
            logger.error(f"Помилка ініціалізації бази даних: {e}")
            raise
    
    async def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Отримує дані гравця з бази"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute(
                    "SELECT * FROM players WHERE user_id = ?",
                    (user_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Помилка отримання гравця {user_id}: {e}")
            return None
    
    async def save_player(self, player_data: Dict[str, Any]) -> bool:
        """Зберігає або оновлює дані гравця"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Перевіряємо чи існує гравець
                cursor = await db.execute(
                    "SELECT user_id FROM players WHERE user_id = ?",
                    (player_data['user_id'],)
                )
                exists = await cursor.fetchone()
                
                if exists:
                    # Оновлюємо існуючого гравця
                    await db.execute('''
                        UPDATE players SET
                            username = ?,
                            character_name = ?,
                            class = ?,
                            level = ?,
                            experience = ?,
                            gold = ?,
                            strength = ?,
                            agility = ?,
                            intelligence = ?,
                            stamina = ?,
                            charisma = ?,
                            free_points = ?,
                            health = ?,
                            max_health = ?,
                            mana = ?,
                            max_mana = ?,
                            equipment = ?,
                            inventory = ?,
                            current_location = ?,
                            quests = ?,
                            achievements = ?,
                            last_daily_reward = ?,
                            monsters_killed = ?,
                            quests_completed = ?,
                            total_gold_earned = ?,
                            total_damage_dealt = ?,
                            total_damage_taken = ?,
                            active_effects = ?,
                            ability_cooldowns = ?,
                            last_login = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (
                        player_data.get('username', ''),
                        player_data.get('character_name', 'Безіменний'),
                        player_data.get('class', 'warrior'),
                        player_data.get('level', 1),
                        player_data.get('experience', 0),
                        player_data.get('gold', 100),
                        player_data.get('strength', 0),
                        player_data.get('agility', 0),
                        player_data.get('intelligence', 0),
                        player_data.get('stamina', 0),
                        player_data.get('charisma', 0),
                        player_data.get('free_points', 5),
                        player_data.get('health', 0),
                        player_data.get('max_health', 0),
                        player_data.get('mana', 0),
                        player_data.get('max_mana', 0),
                        player_data.get('equipment', '{}'),
                        player_data.get('inventory', '[]'),
                        player_data.get('current_location', 'city'),
                        player_data.get('quests', '{}'),
                        player_data.get('achievements', '[]'),
                        player_data.get('last_daily_reward'),
                        player_data.get('monsters_killed', 0),
                        player_data.get('quests_completed', 0),
                        player_data.get('total_gold_earned', 100),
                        player_data.get('total_damage_dealt', 0),
                        player_data.get('total_damage_taken', 0),
                        player_data.get('active_effects', '[]'),
                        player_data.get('ability_cooldowns', '{}'),
                        player_data.get('last_login'),
                        player_data['user_id']
                    ))
                else:
                    # Створюємо нового гравця
                    await db.execute('''
                        INSERT INTO players (
                            user_id, username, character_name, class,
                            level, experience, gold,
                            strength, agility, intelligence, stamina, charisma, free_points,
                            health, max_health, mana, max_mana,
                            equipment, inventory, current_location,
                            quests, achievements, last_daily_reward,
                            monsters_killed, quests_completed, total_gold_earned,
                            total_damage_dealt, total_damage_taken,
                            active_effects, ability_cooldowns, last_login
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        player_data.get('user_id'),
                        player_data.get('username', ''),
                        player_data.get('character_name', 'Безіменний'),
                        player_data.get('class', 'warrior'),
                        player_data.get('level', 1),
                        player_data.get('experience', 0),
                        player_data.get('gold', 100),
                        player_data.get('strength', 0),
                        player_data.get('agility', 0),
                        player_data.get('intelligence', 0),
                        player_data.get('stamina', 0),
                        player_data.get('charisma', 0),
                        player_data.get('free_points', 5),
                        player_data.get('health', 0),
                        player_data.get('max_health', 0),
                        player_data.get('mana', 0),
                        player_data.get('max_mana', 0),
                        player_data.get('equipment', '{}'),
                        player_data.get('inventory', '[]'),
                        player_data.get('current_location', 'city'),
                        player_data.get('quests', '{}'),
                        player_data.get('achievements', '[]'),
                        player_data.get('last_daily_reward'),
                        player_data.get('monsters_killed', 0),
                        player_data.get('quests_completed', 0),
                        player_data.get('total_gold_earned', 100),
                        player_data.get('total_damage_dealt', 0),
                        player_data.get('total_damage_taken', 0),
                        player_data.get('active_effects', '[]'),
                        player_data.get('ability_cooldowns', '{}'),
                        player_data.get('last_login')
                    ))
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Помилка збереження гравця: {e}")
            return False