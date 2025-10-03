# src/config/equipment.py - Розширена система спорядження

from typing import Dict, Any, List

class ItemSlot:
    """Слоти для екіпірування"""
    WEAPON = "weapon"           # Зброя
    HEAD = "head"               # Шолом
    CHEST = "chest"             # Нагрудник
    LEGS = "legs"               # Набедреник (НОВИЙ)
    FEET = "feet"               # Взуття
    HANDS = "hands"             # Рукавиці (НОВИЙ)
    OFFHAND = "offhand"         # Щит/друга рука
    RING_1 = "ring_1"           # Перстень 1 (НОВИЙ)
    RING_2 = "ring_2"           # Перстень 2 (НОВИЙ)
    EARRING_1 = "earring_1"     # Сережка 1 (НОВИЙ)
    EARRING_2 = "earring_2"     # Сережка 2 (НОВИЙ)
    AMULET = "amulet"           # Амулет (НОВИЙ)


class ItemRarity:
    """Рідкість предметів"""
    COMMON = "common"           # Звичайний (білий)
    UNCOMMON = "uncommon"       # Незвичайний (зелений)
    RARE = "rare"               # Рідкісний (синій)
    EPIC = "epic"               # Епічний (фіолетовий)
    LEGENDARY = "legendary"     # Легендарний (помаранчевий)


class WeaponType:
    """Типи зброї"""
    MELEE = "melee"             # Ближня зброя (Сила)
    RANGED = "ranged"           # Дальня зброя (Спритність)
    MAGIC = "magic"             # Магічна зброя (Інтелект)


# Емоджі для рідкості
RARITY_EMOJI = {
    ItemRarity.COMMON: "⚪",
    ItemRarity.UNCOMMON: "🟢",
    ItemRarity.RARE: "🔵",
    ItemRarity.EPIC: "🟣",
    ItemRarity.LEGENDARY: "🟠"
}

# Множники ціни залежно від рідкості
RARITY_PRICE_MULTIPLIER = {
    ItemRarity.COMMON: 1.0,
    ItemRarity.UNCOMMON: 2.0,
    ItemRarity.RARE: 4.0,
    ItemRarity.EPIC: 8.0,
    ItemRarity.LEGENDARY: 15.0
}


# ==================== ЗБРОЯ ====================

WEAPONS: Dict[str, Dict[str, Any]] = {
    # === БЛИЖНЯ ЗБРОЯ (СИЛА) ===
    "rusty_sword": {
        "name": "🗡️ Іржавий меч",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.MELEE,
        "damage_dice": "1d6",  # НОВЕ
        "rarity": ItemRarity.COMMON,
        "level_required": 1,
        "base_price": 50,
        "strength_bonus": 2,
        "description": "Старий, але надійний меч"
    },
    "iron_sword": {
        "name": "⚔️ Залізний меч",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.MELEE,
        "damage_dice": "1d8",  # НОВЕ
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 3,
        "base_price": 150,
        "strength_bonus": 5,
        "description": "Добре збалансований залізний меч"
    },
    "steel_sword": {
        "name": "⚔️ Сталевий меч",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.MELEE,
        "damage_dice": "1d8",  # НОВЕ
        "rarity": ItemRarity.RARE,
        "level_required": 5,
        "base_price": 400,
        "strength_bonus": 8,
        "stamina_bonus": 2,
        "description": "Міцний сталевий меч високої якості"
    },
    "knight_sword": {
        "name": "⚔️ Меч лицаря",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.MELEE,
        "damage_dice": "1d10",  # НОВЕ
        "rarity": ItemRarity.EPIC,
        "level_required": 8,
        "base_price": 1000,
        "strength_bonus": 12,
        "stamina_bonus": 4,
        "description": "Благородний меч відважного лицаря"
    },
    "dragon_slayer": {
        "name": "⚔️ Вбивця драконів",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.MELEE,
        "damage_dice": "2d6",  # НОВЕ
        "rarity": ItemRarity.LEGENDARY,
        "level_required": 12,
        "base_price": 3000,
        "strength_bonus": 18,
        "stamina_bonus": 6,
        "agility_bonus": 3,
        "description": "Легендарний меч, здатний вбити дракона"
    },
    
    # === ДАЛЬНЯ ЗБРОЯ (СПРИТНІСТЬ) ===
    "simple_bow": {
        "name": "🏹 Простий лук",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.RANGED,
        "damage_dice": "1d6",  # НОВЕ
        "rarity": ItemRarity.COMMON,
        "level_required": 1,
        "base_price": 60,
        "agility_bonus": 2,
        "description": "Дерев'яний лук для точних пострілів"
    },
    "hunters_bow": {
        "name": "🏹 Лук мисливця",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.RANGED,
        "damage_dice": "1d8",  # НОВЕ
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 3,
        "base_price": 180,
        "agility_bonus": 5,
        "strength_bonus": 1,
        "description": "Надійний лук досвідченого мисливця"
    },
    "elven_bow": {
        "name": "🏹 Ельфійський лук",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.RANGED,
        "damage_dice": "1d8",  # НОВЕ
        "rarity": ItemRarity.RARE,
        "level_required": 5,
        "base_price": 450,
        "agility_bonus": 9,
        "intelligence_bonus": 2,
        "description": "Витончений лук ельфів"
    },
    "crossbow_master": {
        "name": "🏹 Арбалет майстра",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.RANGED,
        "damage_dice": "1d10",  # НОВЕ
        "rarity": ItemRarity.EPIC,
        "level_required": 8,
        "base_price": 1100,
        "agility_bonus": 13,
        "strength_bonus": 3,
        "description": "Потужний арбалет з точним прицілом"
    },
    
    # === МАГІЧНА ЗБРОЯ (ІНТЕЛЕКТ) ===
    "wooden_staff": {
        "name": "🪄 Дерев'яний посох",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.MAGIC,
        "damage_dice": "1d4",  # НОВЕ
        "rarity": ItemRarity.COMMON,
        "level_required": 1,
        "base_price": 70,
        "intelligence_bonus": 2,
        "description": "Простий посох для початківців магів"
    },
    "apprentice_wand": {
        "name": "✨ Паличка учня",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.MAGIC,
        "damage_dice": "1d6",  # НОВЕ
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 3,
        "base_price": 200,
        "intelligence_bonus": 5,
        "charisma_bonus": 1,
        "description": "Магічна паличка для учнів академії"
    },
    "arcane_staff": {
        "name": "🔮 Таємний посох",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.MAGIC,
        "damage_dice": "1d6",  # НОВЕ
        "rarity": ItemRarity.RARE,
        "level_required": 5,
        "base_price": 500,
        "intelligence_bonus": 9,
        "stamina_bonus": 2,
        "description": "Посох, наповнений таємною енергією"
    },
    "wizards_staff": {
        "name": "🧙 Посох чаклуна",
        "type": "weapon",
        "slot": ItemSlot.WEAPON,
        "weapon_type": WeaponType.MAGIC,
        "damage_dice": "1d8",  # НОВЕ
        "rarity": ItemRarity.EPIC,
        "level_required": 8,
        "base_price": 1200,
        "intelligence_bonus": 14,
        "charisma_bonus": 3,
        "stamina_bonus": 2,
        "description": "Могутній посох досвідченого мага"
    },
}


# ==================== БРОНЯ ====================

ARMOR: Dict[str, Dict[str, Any]] = {
    # === ШОЛОМИ ===
    "leather_cap": {
        "name": "🎩 Шкіряна шапка",
        "type": "armor",
        "slot": ItemSlot.HEAD,
        "rarity": ItemRarity.COMMON,
        "level_required": 1,
        "base_price": 30,
        "stamina_bonus": 1,
        "description": "Проста шкіряна захист для голови"
    },
    "iron_helmet": {
        "name": "⛑️ Залізний шолом",
        "type": "armor",
        "slot": ItemSlot.HEAD,
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 3,
        "base_price": 120,
        "stamina_bonus": 3,
        "strength_bonus": 1,
        "description": "Міцний залізний шолом"
    },
    "steel_helmet": {
        "name": "⛑️ Сталевий шолом",
        "type": "armor",
        "slot": ItemSlot.HEAD,
        "rarity": ItemRarity.RARE,
        "level_required": 5,
        "base_price": 320,
        "stamina_bonus": 5,
        "strength_bonus": 2,
        "description": "Важкий сталевий шолом"
    },
    
    # === НАГРУДНИКИ ===
    "leather_armor": {
        "name": "👕 Шкіряний обладунок",
        "type": "armor",
        "slot": ItemSlot.CHEST,
        "rarity": ItemRarity.COMMON,
        "level_required": 1,
        "base_price": 50,
        "stamina_bonus": 2,
        "agility_bonus": 1,
        "description": "Легкий шкіряний обладунок"
    },
    "chainmail": {
        "name": "⛓️ Кольчуга",
        "type": "armor",
        "slot": ItemSlot.CHEST,
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 3,
        "base_price": 200,
        "stamina_bonus": 5,
        "description": "Надійна металева кольчуга"
    },
    "plate_armor": {
        "name": "🛡️ Латний обладунок",
        "type": "armor",
        "slot": ItemSlot.CHEST,
        "rarity": ItemRarity.RARE,
        "level_required": 5,
        "base_price": 500,
        "stamina_bonus": 8,
        "strength_bonus": 2,
        "description": "Важкий латний обладунок воїна"
    },
    
    # === НАБЕДРЕНИКИ (НОВИЙ СЛОТ) ===
    "leather_pants": {
        "name": "👖 Шкіряні штани",
        "type": "armor",
        "slot": ItemSlot.LEGS,
        "rarity": ItemRarity.COMMON,
        "level_required": 1,
        "base_price": 35,
        "stamina_bonus": 1,
        "agility_bonus": 1,
        "description": "Зручні шкіряні штани"
    },
    "iron_leggings": {
        "name": "🦿 Залізні набедреники",
        "type": "armor",
        "slot": ItemSlot.LEGS,
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 3,
        "base_price": 150,
        "stamina_bonus": 3,
        "strength_bonus": 1,
        "description": "Міцний захист для ніг"
    },
    
    # === ВЗУТТЯ ===
    "simple_boots": {
        "name": "👢 Прості чоботи",
        "type": "armor",
        "slot": ItemSlot.FEET,
        "rarity": ItemRarity.COMMON,
        "level_required": 1,
        "base_price": 25,
        "agility_bonus": 1,
        "description": "Зручні дорожні чоботи"
    },
    "leather_boots": {
        "name": "🥾 Шкіряні чоботи",
        "type": "armor",
        "slot": ItemSlot.FEET,
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 3,
        "base_price": 100,
        "agility_bonus": 3,
        "stamina_bonus": 1,
        "description": "Міцні шкіряні чоботи"
    },
    
    # === РУКАВИЦІ (НОВИЙ СЛОТ) ===
    "cloth_gloves": {
        "name": "🧤 Тканинні рукавиці",
        "type": "armor",
        "slot": ItemSlot.HANDS,
        "rarity": ItemRarity.COMMON,
        "level_required": 1,
        "base_price": 20,
        "agility_bonus": 1,
        "description": "Легкі тканинні рукавиці"
    },
    "leather_gloves": {
        "name": "🧤 Шкіряні рукавиці",
        "type": "armor",
        "slot": ItemSlot.HANDS,
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 3,
        "base_price": 90,
        "agility_bonus": 2,
        "strength_bonus": 1,
        "description": "Міцні шкіряні рукавиці"
    },
    "gauntlets": {
        "name": "🥊 Латні рукавиці",
        "type": "armor",
        "slot": ItemSlot.HANDS,
        "rarity": ItemRarity.RARE,
        "level_required": 5,
        "base_price": 250,
        "strength_bonus": 3,
        "stamina_bonus": 2,
        "description": "Важкі бойові рукавиці"
    },
    
    # === ЩИТ ===
    "wooden_shield": {
        "name": "🛡️ Дерев'яний щит",
        "type": "armor",
        "slot": ItemSlot.OFFHAND,
        "rarity": ItemRarity.COMMON,
        "level_required": 1,
        "base_price": 40,
        "stamina_bonus": 2,
        "description": "Простий дерев'яний щит"
    },
    "iron_shield": {
        "name": "🛡️ Залізний щит",
        "type": "armor",
        "slot": ItemSlot.OFFHAND,
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 3,
        "base_price": 180,
        "stamina_bonus": 4,
        "description": "Важкий залізний щит"
    },
}


# ==================== АКСЕСУАРИ ====================

ACCESSORIES: Dict[str, Dict[str, Any]] = {
    # === ПЕРСТЕНІ ===
    "copper_ring": {
        "name": "💍 Мідний перстень",
        "type": "accessory",
        "slot": ItemSlot.RING_1,  # Можна одягти в будь-який слот кільця
        "rarity": ItemRarity.COMMON,
        "level_required": 2,
        "base_price": 50,
        "strength_bonus": 1,
        "description": "Простий мідний перстень"
    },
    "silver_ring": {
        "name": "💍 Срібний перстень",
        "type": "accessory",
        "slot": ItemSlot.RING_1,
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 4,
        "base_price": 150,
        "agility_bonus": 2,
        "charisma_bonus": 1,
        "description": "Елегантний срібний перстень"
    },
    "gold_ring": {
        "name": "💍 Золотий перстень",
        "type": "accessory",
        "slot": ItemSlot.RING_1,
        "rarity": ItemRarity.RARE,
        "level_required": 6,
        "base_price": 400,
        "intelligence_bonus": 3,
        "charisma_bonus": 2,
        "description": "Коштовний золотий перстень"
    },
    "ring_of_power": {
        "name": "💍 Перстень сили",
        "type": "accessory",
        "slot": ItemSlot.RING_1,
        "rarity": ItemRarity.EPIC,
        "level_required": 8,
        "base_price": 900,
        "strength_bonus": 4,
        "stamina_bonus": 2,
        "description": "Перстень, що збільшує фізичну силу"
    },
    
    # === СЕРЕЖКИ ===
    "simple_earring": {
        "name": "💎 Проста сережка",
        "type": "accessory",
        "slot": ItemSlot.EARRING_1,
        "rarity": ItemRarity.COMMON,
        "level_required": 2,
        "base_price": 40,
        "charisma_bonus": 1,
        "description": "Невелика прикраса"
    },
    "pearl_earring": {
        "name": "💎 Перлинна сережка",
        "type": "accessory",
        "slot": ItemSlot.EARRING_1,
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 4,
        "base_price": 130,
        "intelligence_bonus": 2,
        "charisma_bonus": 1,
        "description": "Сережка з перлиною"
    },
    "diamond_earring": {
        "name": "💎 Діамантова сережка",
        "type": "accessory",
        "slot": ItemSlot.EARRING_1,
        "rarity": ItemRarity.RARE,
        "level_required": 6,
        "base_price": 380,
        "intelligence_bonus": 3,
        "agility_bonus": 2,
        "description": "Розкішна сережка з діамантом"
    },
    
    # === АМУЛЕТИ ===
    "wooden_amulet": {
        "name": "📿 Дерев'яний амулет",
        "type": "accessory",
        "slot": ItemSlot.AMULET,
        "rarity": ItemRarity.COMMON,
        "level_required": 2,
        "base_price": 60,
        "stamina_bonus": 1,
        "intelligence_bonus": 1,
        "description": "Простий захисний амулет"
    },
    "stone_amulet": {
        "name": "📿 Кам'яний амулет",
        "type": "accessory",
        "slot": ItemSlot.AMULET,
        "rarity": ItemRarity.UNCOMMON,
        "level_required": 4,
        "base_price": 170,
        "stamina_bonus": 2,
        "strength_bonus": 2,
        "description": "Амулет з магічним каменем"
    },
    "crystal_amulet": {
        "name": "📿 Кришталевий амулет",
        "type": "accessory",
        "slot": ItemSlot.AMULET,
        "rarity": ItemRarity.RARE,
        "level_required": 6,
        "base_price": 450,
        "intelligence_bonus": 4,
        "stamina_bonus": 2,
        "description": "Амулет з чистого кришталю"
    },
    "dragon_amulet": {
        "name": "📿 Амулет дракона",
        "type": "accessory",
        "slot": ItemSlot.AMULET,
        "rarity": ItemRarity.EPIC,
        "level_required": 9,
        "base_price": 1100,
        "strength_bonus": 3,
        "intelligence_bonus": 3,
        "stamina_bonus": 3,
        "charisma_bonus": 2,
        "description": "Легендарний амулет з силою дракона"
    },
}


# Об'єднуємо всі предмети для магазину
ALL_SHOP_ITEMS = {**WEAPONS, **ARMOR, **ACCESSORIES}


def get_item_price(item: Dict[str, Any]) -> int:
    """Розраховує ціну предмета з урахуванням рідкості"""
    base_price = item.get("base_price", 100)
    rarity = item.get("rarity", ItemRarity.COMMON)
    multiplier = RARITY_PRICE_MULTIPLIER.get(rarity, 1.0)
    return int(base_price * multiplier)


def get_items_by_level(player_level: int) -> Dict[str, Dict[str, Any]]:
    """Повертає предмети, доступні для рівня гравця"""
    available_items = {}
    for item_id, item_data in ALL_SHOP_ITEMS.items():
        if item_data.get("level_required", 1) <= player_level:
            available_items[item_id] = item_data
    return available_items


def format_item_description(item: Dict[str, Any]) -> str:
    """Форматує опис предмета"""
    rarity_emoji = RARITY_EMOJI.get(item.get("rarity", ItemRarity.COMMON), "⚪")
    name = item.get("name", "Предмет")
    description = item.get("description", "")
    level_req = item.get("level_required", 1)
    price = get_item_price(item)
    
    # Бонуси
    bonuses = []
    if item.get("strength_bonus"):
        bonuses.append(f"💪 Сила +{item['strength_bonus']}")
    if item.get("agility_bonus"):
        bonuses.append(f"🏃 Спритність +{item['agility_bonus']}")
    if item.get("intelligence_bonus"):
        bonuses.append(f"🧠 Інтелект +{item['intelligence_bonus']}")
    if item.get("stamina_bonus"):
        bonuses.append(f"🛡️ Витривалість +{item['stamina_bonus']}")
    if item.get("charisma_bonus"):
        bonuses.append(f"✨ Харизма +{item['charisma_bonus']}")
    
    bonus_text = "\n".join(bonuses) if bonuses else "Немає бонусів"
    
    return (
        f"{rarity_emoji} **{name}**\n"
        f"📜 {description}\n"
        f"🎯 Рівень: {level_req}+\n"
        f"💰 Ціна: {price} золота\n\n"
        f"{bonus_text}"
    )