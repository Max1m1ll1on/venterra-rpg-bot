from typing import Dict, Any, Optional
from enum import Enum


class QuestType(Enum):
    """Типи квестів"""
    KILL = "kill"              # Вбити X монстрів
    EXPLORE = "explore"        # Дослідити локацію
    COLLECT = "collect"        # Зібрати предмети
    SURVIVE = "survive"        # Вижити X боїв


class QuestStatus(Enum):
    """Статуси квестів"""
    AVAILABLE = "available"    # Доступний для взяття
    ACTIVE = "active"          # Активний
    COMPLETED = "completed"    # Виконаний
    CLAIMED = "claimed"        # Винагорода отримана


class Quest:
    """Модель квесту"""
    
    def __init__(self, quest_id: str, quest_data: Dict[str, Any]):
        self.quest_id = quest_id
        self.name = quest_data["name"]
        self.description = quest_data["description"]
        self.quest_type = QuestType(quest_data["type"])
        self.level_required = quest_data.get("level_required", 1)
        
        # Цілі
        self.target = quest_data["target"]  # Скільки треба
        self.target_detail = quest_data.get("target_detail")  # Що саме (тип монстра, локація)
        
        # Прогрес
        self.progress = 0
        self.status = QuestStatus.AVAILABLE
        
        # Винагороди
        self.rewards = quest_data["rewards"]
    
    def update_progress(self, amount: int = 1) -> bool:
        """Оновлює прогрес квесту"""
        if self.status != QuestStatus.ACTIVE:
            return False
        
        self.progress += amount
        
        # Перевіряємо чи виконано
        if self.progress >= self.target:
            self.progress = self.target
            self.status = QuestStatus.COMPLETED
            return True
        
        return False
    
    def is_completed(self) -> bool:
        """Перевіряє чи квест виконано"""
        return self.status == QuestStatus.COMPLETED
    
    def can_claim_reward(self) -> bool:
        """Перевіряє чи можна отримати винагороду"""
        return self.status == QuestStatus.COMPLETED
    
    def claim_reward(self) -> bool:
        """Отримує винагороду"""
        if not self.can_claim_reward():
            return False
        
        self.status = QuestStatus.CLAIMED
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертує у словник"""
        return {
            "quest_id": self.quest_id,
            "name": self.name,
            "description": self.description,
            "type": self.quest_type.value,
            "level_required": self.level_required,
            "target": self.target,
            "target_detail": self.target_detail,
            "progress": self.progress,
            "status": self.status.value,
            "rewards": self.rewards
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quest":
        """Створює квест зі словника"""
        quest = cls(data["quest_id"], data)
        quest.progress = data.get("progress", 0)
        quest.status = QuestStatus(data.get("status", "available"))
        return quest