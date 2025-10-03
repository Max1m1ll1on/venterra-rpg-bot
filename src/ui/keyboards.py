# src/ui/keyboards.py - Клавіатури інтерфейсу

from aiogram import types
from src.config.constants import CLASS_NAMES, CharacterClass


def get_class_selection_keyboard() -> types.InlineKeyboardMarkup:
    """Клавіатура вибору класу персонажа"""
    buttons = []
    
    for class_id in CharacterClass.ALL:
        class_name = CLASS_NAMES[class_id]
        buttons.append([
            types.InlineKeyboardButton(
                text=class_name,
                callback_data=f"create_{class_id}"
            )
        ])
    
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def get_adventure_main_keyboard() -> types.ReplyKeyboardMarkup:
    """Клавіатура під час пригод (поза містом)"""
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="👤 Персонаж"),
                types.KeyboardButton(text="🎒 Інвентар")
            ],
            [
                types.KeyboardButton(text="🏰 Повернутися до міста"),
                types.KeyboardButton(text="🗺️ Досліджувати") 
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_city_keyboard() -> types.ReplyKeyboardMarkup:
    """Головна клавіатура міста"""
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="🏪 Магазин"),
                types.KeyboardButton(text="🏰 Гільдія")
            ],
            [
                types.KeyboardButton(text="🍺 Таверна"),
                types.KeyboardButton(text="⚕️ Лікар")
            ],
            [
                types.KeyboardButton(text="⛪ Храм"),
                types.KeyboardButton(text="👤 Персонаж")
            ],
            [
                types.KeyboardButton(text="🎒 Інвентар"),
                types.KeyboardButton(text="🌲 Пригоди")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_adventures_keyboard(player_level: int = 1) -> types.InlineKeyboardMarkup:
    """Клавіатура вибору локації для пригод"""
    from src.config.constants import LOCATIONS, Location
    
    buttons = []
    
    # Додаємо локації згідно рівня
    available_locations = [
        (Location.FOREST, 1),
        (Location.MOUNTAINS, 2),
        (Location.RUINS, 3),
        (Location.CAVES, 4),
        (Location.SWAMP, 5),
    ]
    
    for location_id, min_level in available_locations:
        location = LOCATIONS[location_id]
        
        if player_level >= min_level:
            button_text = f"{location['emoji']} {location['name']}"
            callback_data = f"explore_{location_id}"
        else:
            button_text = f"{location['emoji']} {location['name']} (Рів. {min_level}+)"
            callback_data = f"locked_{location_id}"
        
        buttons.append([
            types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
        ])
    
    # ВИДАЛЕНО: Кнопка повернення (використовуємо звичайну кнопку замість inline)
    
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def get_battle_keyboard() -> types.InlineKeyboardMarkup:
    """Клавіатура бою"""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⚔️ Атакувати", callback_data="battle_attack")],
        [types.InlineKeyboardButton(text="🛡️ Захищатися", callback_data="battle_defend")],
        [types.InlineKeyboardButton(text="💨 Втекти", callback_data="battle_flee")]
    ])
    return keyboard


def get_victory_keyboard() -> types.InlineKeyboardMarkup:
    """Клавіатура після перемоги"""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🌲 Продовжити дослідження", callback_data="continue_adventure")
        ]
    ])
    return keyboard


def get_shop_keyboard() -> types.InlineKeyboardMarkup:
    """Клавіатура магазину"""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🗡️ Зброя", callback_data="shop_weapons")],
        [types.InlineKeyboardButton(text="🛡️ Броня", callback_data="shop_armor")],
        [types.InlineKeyboardButton(text="🧪 Зілля", callback_data="shop_potions")],
        [types.InlineKeyboardButton(text="💰 Продати", callback_data="shop_sell")],
        [types.InlineKeyboardButton(text="🚪 Вийти", callback_data="leave_shop")]
    ])
    return keyboard


def get_inventory_keyboard() -> types.InlineKeyboardMarkup:
    """Клавіатура інвентаря"""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⚔️ Спорядження", callback_data="inv_equipment")],
        [types.InlineKeyboardButton(text="🧪 Зілля", callback_data="inv_potions")],
        [types.InlineKeyboardButton(text="📦 Інше", callback_data="inv_other")],
        [types.InlineKeyboardButton(text="🚪 Закрити", callback_data="inv_close")]
    ])
    return keyboard


def get_character_keyboard() -> types.InlineKeyboardMarkup:
    """Клавіатура персонажа"""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📊 Статистика", callback_data="char_stats")],
        [types.InlineKeyboardButton(text="🎯 Квести", callback_data="char_quests")],
        [types.InlineKeyboardButton(text="🏆 Досягнення", callback_data="char_achievements")]
    ])
    return keyboard


def get_stats_distribution_keyboard() -> types.InlineKeyboardMarkup:
    """Клавіатура розподілу статів"""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="💪 Сила", callback_data="stat_strength"),
            types.InlineKeyboardButton(text="🏃 Спритність", callback_data="stat_agility")
        ],
        [
            types.InlineKeyboardButton(text="🧠 Інтелект", callback_data="stat_intelligence"),
            types.InlineKeyboardButton(text="🛡️ Витривалість", callback_data="stat_stamina")
        ],
        [
            types.InlineKeyboardButton(text="🎭 Харизма", callback_data="stat_charisma")
        ],
        [
            types.InlineKeyboardButton(text="✅ Завершити", callback_data="stats_done")
        ]
    ])
    return keyboard