# src/config/constants.py - Ігрові константи

from typing import Dict, Any

# ==================== КЛАСИ ПЕРСОНАЖІВ ====================

class CharacterClass:
    """Константи класів персонажів"""
    WARRIOR = "warrior"
    MAGE = "mage"
    PALADIN = "paladin"
    ROGUE = "rogue"
    
    ALL = [WARRIOR, MAGE, PALADIN, ROGUE]


# Базові характеристики класів (25 ОЧОК НА СТАРТІ)
CLASS_BASE_STATS: Dict[str, Dict[str, int]] = {
    CharacterClass.WARRIOR: {
        "strength": 8,      # Сила - головна
        "agility": 5,
        "intelligence": 3,
        "stamina": 7,       # Витривалість
        "charisma": 2,
    },
    CharacterClass.MAGE: {
        "strength": 2,
        "agility": 4,
        "intelligence": 10,  # Інтелект - головна
        "stamina": 5,
        "charisma": 4,
    },
    CharacterClass.PALADIN: {
        "strength": 6,
        "agility": 4,
        "intelligence": 5,
        "stamina": 6,
        "charisma": 4,
    },
    CharacterClass.ROGUE: {
        "strength": 4,
        "agility": 9,        # Спритність - головна
        "intelligence": 3,
        "stamina": 5,
        "charisma": 4,
    },
}

# Назви класів українською
CLASS_NAMES: Dict[str, str] = {
    CharacterClass.WARRIOR: "⚔️ Воїн",
    CharacterClass.MAGE: "🔮 Маг",
    CharacterClass.PALADIN: "🛡️ Паладин",
    CharacterClass.ROGUE: "🏹 Розбійник",
}

# Описи класів
CLASS_DESCRIPTIONS: Dict[str, str] = {
    CharacterClass.WARRIOR: (
        "Майстер ближнього бою. Володієте мечем та щитом, "
        "маєте високу витривалість та силу. Ідеальний вибір для тих, "
        "хто любить прямий бій."
    ),
    CharacterClass.MAGE: (
        "Володар стихій. Керуєте магією вогню, льоду та блискавок. "
        "Хоч ви не дуже міцні, ваша сила у потужних заклинаннях."
    ),
    CharacterClass.PALADIN: (
        "Святий воїн. Поєднуєте бойову майстерність з "
        "цілющою магією. Збалансований клас для універсальних гравців."
    ),
    CharacterClass.ROGUE: (
        "Майстер тіні. Швидкі, спритні та вмієте завдавати "
        "критичні удари. Покладайтесь на хитрість, а не на грубу силу."
    ),
}


# ==================== ЛОКАЦІЇ ====================

class Location:
    """Константи локацій"""
    CITY = "city"
    FOREST = "forest"
    MOUNTAINS = "mountains"
    RUINS = "ruins"
    CAVES = "caves"
    SWAMP = "swamp"
    VOLCANO = "volcano"
    ICE_PEAKS = "ice_peaks"
    CASTLE = "ancient_castle"


# Дані локацій
LOCATIONS: Dict[str, Dict[str, Any]] = {
    Location.CITY: {
        "name": "🏰 Місто StaryFall",
        "description": "Процвітаюче торгове місто в центрі королівства Crys",
        "level_required": 1,
        "emoji": "🏰",
        "safe": True,
    },
    Location.FOREST: {
        "name": "🌳 Зелений ліс",
        "description": "Густий ліс, повний диких тварин та прихованих скарбів",
        "level_required": 1,
        "emoji": "🌳",
        "monsters": ["wolf", "spider"],
    },
    Location.MOUNTAINS: {
        "name": "🏔️ Кам'яні гори",
        "description": "Високі гори, де мешкають небезпечні істоти",
        "level_required": 2,
        "emoji": "🏔️",
        "monsters": ["bandit", "orc"],
    },
    Location.RUINS: {
        "name": "🏚️ Стародавні руїни",
        "description": "Залишки забутої цивілізації, повні магії та небезпек",
        "level_required": 3,
        "emoji": "🏚️",
        "monsters": ["skeleton", "wizard"],
    },
    Location.CAVES: {
        "name": "🕳️ Глибокі печери",
        "description": "Темні печери з підземними озерами та дивними істотами",
        "level_required": 4,
        "emoji": "🕳️",
        "monsters": ["goblin", "spider", "orc"],
    },
    Location.SWAMP: {
        "name": "🐊 Мертві болота",
        "description": "Заболочена місцевість, де блукає нежить",
        "level_required": 5,
        "emoji": "🐊",
        "monsters": ["skeleton", "wizard", "spider"],
    },
}


# ==================== МОНСТРИ ====================

class MonsterType:
    """Типи монстрів"""
    WOLF = "wolf"
    SPIDER = "spider"
    GOBLIN = "goblin"
    SKELETON = "skeleton"
    BANDIT = "bandit"
    ORC = "orc"
    WIZARD = "wizard"
    DRAGON = "dragon"


# Базові характеристики монстрів
MONSTER_BASE_STATS: Dict[str, Dict[str, Any]] = {
    MonsterType.WOLF: {
        "name": "🐺 Вовк",
        "health": 25,      # Було: 30 → Зменшено на 17%
        "attack": 6,       # Було: 8 → Зменшено на 25%
        "defense": 2,      # Було: 3 → Зменшено на 33%
        "exp_reward": 50,
        "gold_reward": 10,
        "loot": ["🐺 Вовчий ікло", "🐺 Вовча шкура"],
        "loot_chance": 0.7,
    },
    MonsterType.SPIDER: {
        "name": "🕷️ Гігантський павук",
        "health": 16,      # Було: 20 → Зменшено на 20%
        "attack": 5,       # Було: 7 → Зменшено на 29%
        "defense": 1,      # Без змін (вже 1)
        "exp_reward": 40,
        "gold_reward": 8,
        "loot": ["🕸️ Павутиння", "☠️ Отрута павука"],
        "loot_chance": 0.6,
    },
    MonsterType.GOBLIN: {
        "name": "👹 Гоблін",
        "health": 20,      # Було: 25 → Зменшено на 20%
        "attack": 5,       # Було: 6 → Зменшено на 17%
        "defense": 2,      # Без змін
        "exp_reward": 60,
        "gold_reward": 15,
        "loot": ["👹 Вухо гобліна", "🪙 Мішок золота"],
        "loot_chance": 0.8,
    },
    
    # Монстри 3+ рівня БЕЗ ЗМІН:
    MonsterType.SKELETON: {
        "name": "💀 Скелет-воїн",
        "health": 35,
        "attack": 9,
        "defense": 4,
        "exp_reward": 80,
        "gold_reward": 20,
        "loot": ["🦴 Кістка", "⚔️ Стара зброя"],
        "loot_chance": 0.5,
    },
    MonsterType.BANDIT: {
        "name": "🏹 Бандит",
        "health": 40,
        "attack": 10,
        "defense": 5,
        "exp_reward": 100,
        "gold_reward": 25,
        "loot": ["🏹 Стріли", "💼 Шкіряний гаманець"],
        "loot_chance": 0.9,
    },
    MonsterType.ORC: {
        "name": "👹 Орк-берсерк",
        "health": 50,
        "attack": 12,
        "defense": 6,
        "exp_reward": 120,
        "gold_reward": 30,
        "loot": ["⚔️ Важкий меч", "🛡️ Щит орка"],
        "loot_chance": 0.6,
    },
    MonsterType.WIZARD: {
        "name": "🧙 Темний маг",
        "health": 30,
        "attack": 14,
        "defense": 3,
        "exp_reward": 150,
        "gold_reward": 40,
        "loot": ["📜 Сувій", "🔮 Магічний кристал"],
        "loot_chance": 0.8,
    },
    MonsterType.DRAGON: {
        "name": "🐉 Молодий дракон",
        "health": 100,
        "attack": 18,
        "defense": 10,
        "exp_reward": 300,
        "gold_reward": 100,
        "loot": ["💎 Драконяча луска", "🔥 Драконяче серце"],
        "loot_chance": 0.9,
    },
}


# ==================== ПРЕДМЕТИ ====================

class ItemType:
    """Типи предметів"""
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    MATERIAL = "material"
    QUEST = "quest"


class ItemSlot:
    """Слоти для екіпірування"""
    WEAPON = "weapon"
    HEAD = "head"
    CHEST = "chest"
    FEET = "feet"
    OFFHAND = "offhand"


# ==================== КВЕСТИ ====================

class QuestType:
    """Типи квестів"""
    KILL = "kill"
    COLLECT = "collect"
    EXPLORE = "explore"
    TALK = "talk"


class QuestStatus:
    """Статуси квестів"""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


# ==================== БОЙОВА СИСТЕМА ====================

# Шанси у бою (у відсотках)
CRITICAL_HIT_CHANCE = 5  # 5% базовий шанс криту
CRITICAL_HIT_MULTIPLIER = 2.0  # Множник критичного удару

DODGE_BASE_CHANCE = 5  # 5% базовий шанс ухилення
DODGE_PER_AGILITY = 0.5  # +0.5% за кожну одиницю спритності

FLEE_BASE_CHANCE = 40  # 40% базовий шанс втечі
FLEE_PER_AGILITY = 5  # +5% за кожну одиницю спритності
FLEE_MAX_CHANCE = 80  # Максимальний шанс втечі 80%


# ==================== ЕКОНОМІКА ====================

# Ціни предметів у магазині
SHOP_ITEMS: Dict[str, Dict[str, Any]] = {
    "rusty_sword": {
        "name": "🗡️ Іржавий меч",
        "type": ItemType.WEAPON,
        "slot": ItemSlot.WEAPON,
        "price": 50,
        "strength_bonus": 2,
        "description": "Старий, але надійний меч",
    },
    "simple_bow": {
        "name": "🏹 Простий лук",
        "type": ItemType.WEAPON,
        "slot": ItemSlot.WEAPON,
        "price": 60,
        "agility_bonus": 2,
        "description": "Дерев'яний лук для точних пострілів",
    },
    "wooden_shield": {
        "name": "🛡️ Дерев'яний щит",
        "type": ItemType.ARMOR,
        "slot": ItemSlot.OFFHAND,
        "price": 40,
        "stamina_bonus": 2,
        "description": "Простий дерев'яний щит",
    },
    "health_potion": {
        "name": "❤️ Зілля здоров'я",
        "type": ItemType.POTION,
        "price": 25,
        "effect_type": "heal",
        "effect_value": 50,
        "description": "Відновлює 50 HP",
    },
}


# ==================== ІНШЕ ====================

# Множники для храму
TEMPLE_COST_PER_LEVEL = 1.1  # Ціна зростає на 10% за рівень

