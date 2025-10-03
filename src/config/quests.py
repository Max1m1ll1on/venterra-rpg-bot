from typing import Dict, Optional, Any
from src.models.quest import QuestType

# База квестів
AVAILABLE_QUESTS = {
    # ========== КВЕСТИ 1 РІВНЯ ==========
    "first_blood": {
        "name": "🗡️ Перша кров",
        "description": "Вбийте свого першого монстра, щоб довести свою відвагу!",
        "type": QuestType.KILL.value,
        "level_required": 1,
        "target": 1,
        "target_detail": None,  # Будь-який монстр
        "rewards": {
            "exp": 50,
            "gold": 25,
            "message": "Ви довели що готові до пригод!"
        }
    },
    
    "wolf_hunter": {
        "name": "🐺 Полювання на вовків",
        "description": "Вовки нападають на мандрівників. Вбийте 5 вовків.",
        "type": QuestType.KILL.value,
        "level_required": 1,
        "target": 5,
        "target_detail": "wolf",  # Тільки вовки
        "rewards": {
            "exp": 100,
            "gold": 50,
            "message": "Ліс став безпечнішим завдяки вам!"
        }
    },
    
    "forest_explorer": {
        "name": "🌳 Дослідник лісу",
        "description": "Дослідіть ліс та виживіть у 3 боях.",
        "type": QuestType.SURVIVE.value,
        "level_required": 1,
        "target": 3,
        "target_detail": "forest",
        "rewards": {
            "exp": 80,
            "gold": 40,
            "message": "Ви дослідили ліс!"
        }
    },
    
    # ========== КВЕСТИ 2 РІВНЯ ==========
    "spider_menace": {
        "name": "🕷️ Павуча загроза",
        "description": "Гігантські павуки розплодились у лісі. Знищіть 8 павуків.",
        "type": QuestType.KILL.value,
        "level_required": 2,
        "target": 8,
        "target_detail": "spider",
        "rewards": {
            "exp": 150,
            "gold": 60,
            "item": "uncommon",
            "message": "Павучі гнізда знищені!"
        }
    },
    
    "mountain_challenge": {
        "name": "🏔️ Виклик гір",
        "description": "Піднесіться в гори та переможіть у 5 боях.",
        "type": QuestType.SURVIVE.value,
        "level_required": 2,
        "target": 5,
        "target_detail": "mountains",
        "rewards": {
            "exp": 120,
            "gold": 70,
            "message": "Ви підкорили гори!"
        }
    },
    
    # ========== КВЕСТИ 3 РІВНЯ ==========
    "goblin_raid": {
        "name": "👹 Гоблінський набіг",
        "description": "Гобліни грабують караvани. Вбийте 10 гоблінів.",
        "type": QuestType.KILL.value,
        "level_required": 3,
        "target": 10,
        "target_detail": "goblin",
        "rewards": {
            "exp": 200,
            "gold": 100,
            "item": "rare",
            "message": "Гоблінську банду розбито!"
        }
    },
    
    "ruins_explorer": {
        "name": "🏚️ Дослідник руїн",
        "description": "Дослідіть стародавні руїни. Виживіть у 7 боях.",
        "type": QuestType.SURVIVE.value,
        "level_required": 3,
        "target": 7,
        "target_detail": "ruins",
        "rewards": {
            "exp": 180,
            "gold": 90,
            "message": "Таємниці руїн розкриті!"
        }
    },
    
    # ========== КВЕСТИ 4+ РІВНЯ ==========
    "skeleton_army": {
        "name": "💀 Армія нежиті",
        "description": "Некромант підняв армію скелетів. Знищіть 15 скелетів.",
        "type": QuestType.KILL.value,
        "level_required": 4,
        "target": 15,
        "target_detail": "skeleton",
        "rewards": {
            "exp": 300,
            "gold": 150,
            "item": "epic",
            "message": "Некромант втратив свою армію!"
        }
    },
    
    "cave_delver": {
        "name": "🕳️ Спелеолог",
        "description": "Спустіться у глибокі печери. Виживіть у 10 боях.",
        "type": QuestType.SURVIVE.value,
        "level_required": 4,
        "target": 10,
        "target_detail": "caves",
        "rewards": {
            "exp": 250,
            "gold": 120,
            "item": "rare",
            "message": "Ви дослідили найтемніші печери!"
        }
    },
}


def get_available_quests_for_level(level: int) -> Dict[str, Dict]:
    """Повертає квести доступні для рівня"""
    return {
        quest_id: quest_data
        for quest_id, quest_data in AVAILABLE_QUESTS.items()
        if quest_data["level_required"] <= level
    }


def get_quest_by_id(quest_id: str) -> Optional[Dict]:
    """Отримує квест за ID"""
    return AVAILABLE_QUESTS.get(quest_id)