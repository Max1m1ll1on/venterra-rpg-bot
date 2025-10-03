# src/models/monster.py - Модель монстра

import random
from typing import List, Dict
from src.config.constants import MONSTER_BASE_STATS


class Monster:
    """Модель монстра"""
    
    def __init__(self, monster_type: str, level: int = 1):
        """
        Створює монстра
        
        Args:
            monster_type: Тип монстра (wolf, goblin, тощо)
            level: Рівень монстра
        """
        # Отримуємо базові характеристики
        base_stats = MONSTER_BASE_STATS.get(monster_type, MONSTER_BASE_STATS["wolf"])
        
        self.monster_type = monster_type
        self.name = base_stats["name"]
        self.level = level
        
        # Характеристики масштабуються з рівнем
        self.max_health = base_stats["health"] + (level - 1) * 10
        self.health = self.max_health
        self.attack = base_stats["attack"] + (level - 1) * 2
        self.defense = base_stats["defense"] + (level - 1)
        
        # Нагороди
        self.exp_reward = base_stats["exp_reward"] + (level - 1) * 20
        self.gold_reward = base_stats["gold_reward"] + (level - 1) * 5
        
        # Лут
        self.loot_table = base_stats.get("loot", [])
    
    def take_damage(self, amount: int) -> int:
        """
        Отримує урон
        
        Args:
            amount: Кількість урону
            
        Returns:
            Фактично отриманий урон
        """
        # Враховуємо захист
        actual_damage = max(1, amount - self.defense // 2)
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def is_alive(self) -> bool:
        """Перевіряє чи живий монстр"""
        return self.health > 0
    
    def get_loot(self) -> List[str]:
        """
        Генерує лут з монстра
        
        Returns:
            Список предметів
        """
        loot = []
        
        # Шанс випадання кожного предмета 70%
        for item in self.loot_table:
            if random.random() < 0.7:
                loot.append(item)
        
        return loot
    
    def to_dict(self) -> Dict:
        """Конвертує у словник"""
        return {
            "monster_type": self.monster_type,
            "name": self.name,
            "level": self.level,
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "defense": self.defense,
            "exp_reward": self.exp_reward,
            "gold_reward": self.gold_reward,
        }
