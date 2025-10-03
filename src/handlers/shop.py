# src/handlers/shop.py - Оновлений магазин

import logging
from aiogram import Router, F, types

from src.database import Database
from src.models.player import Player
from src.config.equipment import (
    ALL_SHOP_ITEMS, get_item_price, get_items_by_level,
    format_item_description, RARITY_EMOJI, ItemRarity
)
from src.ui.keyboards import get_city_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "🏪 Магазин")
async def show_shop(message: types.Message):
    """Показує головне меню магазину"""
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if not player_data:
        await message.answer("❌ Персонаж не знайдено. Використайте /start")
        return
    
    player = Player.from_dict(player_data)
    
    shop_text = (
        f"🏪 **Магазин StaryFall**\n\n"
        f"Вітаємо, {player.character_name}!\n"
        f"💰 Ваше золото: {player.gold}\n"
        f"🎯 Рівень: {player.level}\n\n"
        f"Оберіть категорію:"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="⚔️ Зброя", callback_data="shop_weapons"),
            types.InlineKeyboardButton(text="🛡️ Броня", callback_data="shop_armor")
        ],
        [
            types.InlineKeyboardButton(text="💍 Аксесуари", callback_data="shop_accessories")
        ],
        [
            types.InlineKeyboardButton(text="💰 Продати предмети", callback_data="shop_sell")
        ]
    ])
    
    await message.answer(shop_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "shop_weapons")
async def show_weapons(callback: types.CallbackQuery):
    """Показує зброю в магазині"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # ПОКАЗУЄМО ВСЮ зброю
    from src.config.equipment import WEAPONS
    
    if not WEAPONS:
        await callback.answer("Немає зброї в асортименті!", show_alert=True)
        return
    
    text = f"⚔️ **Зброя**\n💰 Золото: {player.gold}\n🎯 Рівень: {player.level}\n\n"
    keyboard_buttons = []
    
    for item_id, item_data in list(WEAPONS.items())[:20]:
        rarity_emoji = RARITY_EMOJI.get(item_data.get("rarity", ItemRarity.COMMON), "⚪")
        name = item_data.get("name", "Предмет")
        price = get_item_price(item_data)
        level_req = item_data.get("level_required", 1)
        
        # Перевіряємо чи доступний
        if player.level >= level_req:
            button_text = f"{rarity_emoji} {name} - {price}💰"
        else:
            button_text = f"🔒 {name} - {price}💰 (Рів.{level_req})"
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"shop_view_{item_id}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="shop_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "shop_armor")
async def show_armor(callback: types.CallbackQuery):
    """Показує броню в магазині"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # ПОКАЗУЄМО ВСЮ броню
    from src.config.equipment import ARMOR
    
    if not ARMOR:
        await callback.answer("Немає броні в асортименті!", show_alert=True)
        return
    
    text = f"🛡️ **Броня**\n💰 Золото: {player.gold}\n🎯 Рівень: {player.level}\n\n"
    keyboard_buttons = []
    
    for item_id, item_data in list(ARMOR.items())[:20]:
        rarity_emoji = RARITY_EMOJI.get(item_data.get("rarity", ItemRarity.COMMON), "⚪")
        name = item_data.get("name", "Предмет")
        price = get_item_price(item_data)
        level_req = item_data.get("level_required", 1)
        
        # Перевіряємо чи доступний
        if player.level >= level_req:
            button_text = f"{rarity_emoji} {name} - {price}💰"
        else:
            button_text = f"🔒 {name} - {price}💰 (Рів.{level_req})"
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"shop_view_{item_id}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="shop_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "shop_accessories")
async def show_accessories(callback: types.CallbackQuery):
    """Показує аксесуари в магазині"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # ПОКАЗУЄМО ВСІ аксесуари, а не тільки доступні
    from src.config.equipment import ACCESSORIES
    
    if not ACCESSORIES:
        await callback.answer("Немає аксесуарів в асортименті!", show_alert=True)
        return
    
    text = f"💍 **Аксесуари**\n💰 Золото: {player.gold}\n🎯 Рівень: {player.level}\n\n"
    keyboard_buttons = []
    
    for item_id, item_data in list(ACCESSORIES.items())[:20]:
        rarity_emoji = RARITY_EMOJI.get(item_data.get("rarity", ItemRarity.COMMON), "⚪")
        name = item_data.get("name", "Предмет")
        price = get_item_price(item_data)
        level_req = item_data.get("level_required", 1)
        
        # Перевіряємо чи доступний
        if player.level >= level_req:
            button_text = f"{rarity_emoji} {name} - {price}💰"
        else:
            button_text = f"🔒 {name} - {price}💰 (Рів.{level_req})"
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"shop_view_{item_id}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="shop_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("shop_view_"))
async def view_item(callback: types.CallbackQuery):
    """Показує детальну інформацію про предмет"""
    item_id = callback.data.replace("shop_view_", "")
    
    if item_id not in ALL_SHOP_ITEMS:
        await callback.answer("❌ Предмет не знайдено!")
        return
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    item_data = ALL_SHOP_ITEMS[item_id]
    price = get_item_price(item_data)
    
    item_text = format_item_description(item_data)
    item_text += f"\n\n💰 Ваше золото: {player.gold}"
    
    # Перевірки
    can_buy = True
    reason = ""
    
    if player.gold < price:
        can_buy = False
        reason = "❌ Недостатньо золота"
    elif player.level < item_data.get("level_required", 1):
        can_buy = False
        reason = f"❌ Потрібен {item_data['level_required']} рівень"
    
    keyboard_buttons = []
    
    if can_buy:
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"💰 Купити за {price} золота",
                callback_data=f"shop_buy_{item_id}"
            )
        ])
    else:
        item_text += f"\n\n{reason}"
    
    # Визначаємо назад куди повертатись
    item_type = item_data.get("type")
    if item_type == "weapon":
        back_callback = "shop_weapons"
    elif item_type == "armor":
        back_callback = "shop_armor"
    elif item_type == "accessory":
        back_callback = "shop_accessories"
    else:
        back_callback = "shop_back"
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback)
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(item_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("shop_buy_"))
async def buy_item(callback: types.CallbackQuery):
    """Купує предмет"""
    item_id = callback.data.replace("shop_buy_", "")
    
    if item_id not in ALL_SHOP_ITEMS:
        await callback.answer("❌ Предмет не знайдено!")
        return
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    item_data = ALL_SHOP_ITEMS[item_id].copy()
    price = get_item_price(item_data)
    
    # Перевірки
    if player.gold < price:
        await callback.answer("❌ Недостатньо золота!", show_alert=True)
        return
    
    if player.level < item_data.get("level_required", 1):
        await callback.answer(f"❌ Потрібен {item_data['level_required']} рівень!", show_alert=True)
        return
    
    # Купуємо
    player.gold -= price
    player.inventory.append(item_data)
    
    await db.save_player(player.to_dict())
    
    await callback.answer(f"✅ Куплено {item_data['name']}!", show_alert=True)
    
    # Повертаємось до магазину
    await shop_back(callback)


@router.callback_query(F.data == "shop_back")
async def shop_back(callback: types.CallbackQuery):
    """Повертає до головного меню магазину"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка! Спробуйте ще раз.", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    shop_text = (
        f"🏪 **Магазин StaryFall**\n\n"
        f"Вітаємо, {player.character_name}!\n"
        f"💰 Ваше золото: {player.gold}\n"
        f"🎯 Рівень: {player.level}\n\n"
        f"Оберіть категорію:"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="⚔️ Зброя", callback_data="shop_weapons"),
            types.InlineKeyboardButton(text="🛡️ Броня", callback_data="shop_armor")
        ],
        [
            types.InlineKeyboardButton(text="💍 Аксесуари", callback_data="shop_accessories")
        ],
        [
            types.InlineKeyboardButton(text="💰 Продати предмети", callback_data="shop_sell")
        ]
    ])
    
    await callback.message.edit_text(shop_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "shop_potions")
async def show_potions(callback: types.CallbackQuery):
    """Показує зілля в магазині"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    potions = {
        "health_potion": {
            "name": "❤️ Зілля здоров'я",
            "type": "potion",
            "price": 25,
            "effect_type": "heal",
            "effect_value": 50,
            "description": "Відновлює 50 HP"
        },
        "greater_health_potion": {
            "name": "❤️ Велике зілля здоров'я",
            "type": "potion",
            "price": 50,
            "effect_type": "heal",
            "effect_value": 100,
            "description": "Відновлює 100 HP"
        },
        "full_heal_potion": {
            "name": "✨ Зілля повного відновлення",
            "type": "potion",
            "price": 100,
            "effect_type": "full_heal",
            "description": "Повністю відновлює HP"
        }
    }
    
    text = f"🧪 **Зілля**\n💰 Золото: {player.gold}\n\n"
    keyboard_buttons = []
    
    for potion_id, potion_data in potions.items():
        name = potion_data.get("name", "Зілля")
        price = potion_data.get("price", 25)
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"{name} - {price}💰",
                callback_data=f"shop_buy_potion_{potion_id}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="shop_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("shop_buy_potion_"))
async def buy_potion(callback: types.CallbackQuery):
    """Купує зілля"""
    potion_id = callback.data.replace("shop_buy_potion_", "")
    
    potions = {
        "health_potion": {
            "name": "❤️ Зілля здоров'я",
            "type": "potion",
            "price": 25,
            "effect_type": "heal",
            "effect_value": 50,
            "description": "Відновлює 50 HP"
        },
        "greater_health_potion": {
            "name": "❤️ Велике зілля здоров'я",
            "type": "potion",
            "price": 50,
            "effect_type": "heal",
            "effect_value": 100,
            "description": "Відновлює 100 HP"
        },
        "full_heal_potion": {
            "name": "✨ Зілля повного відновлення",
            "type": "potion",
            "price": 100,
            "effect_type": "full_heal",
            "description": "Повністю відновлює HP"
        }
    }
    
    if potion_id not in potions:
        await callback.answer("❌ Зілля не знайдено!")
        return
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    potion_data = potions[potion_id].copy()
    price = potion_data.get("price", 25)
    
    if player.gold < price:
        await callback.answer("❌ Недостатньо золота!", show_alert=True)
        return
    
    # Купуємо
    player.gold -= price
    player.inventory.append(potion_data)
    
    await db.save_player(player.to_dict())
    
    await callback.answer(f"✅ Куплено {potion_data['name']}!", show_alert=True)
    
@router.callback_query(F.data == "shop_sell")
async def show_sell_menu(callback: types.CallbackQuery):
    """Показує меню продажу"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Збираємо предмети для продажу (не зілля)
    sellable_items = []
    for i, item in enumerate(player.inventory):
        if isinstance(item, dict) and item.get("type") != "potion":
            sellable_items.append((i, item))
    
    if not sellable_items:
        await callback.answer("❌ Немає предметів для продажу!", show_alert=True)
        return
    
    text = f"💰 **Продаж предметів**\n\nВаше золото: {player.gold}\n\n📦 Доступно для продажу: {len(sellable_items)}\n\n"
    keyboard_buttons = []
    
    for index, item in sellable_items[:10]:  # Показуємо перші 10
        name = item.get("name", "Предмет")
        # Ціна продажу = 50% від покупки
        base_price = item.get("base_price", 10)
        from src.config.equipment import RARITY_PRICE_MULTIPLIER, RARITY_EMOJI
        rarity = item.get("rarity", "common")
        multiplier = RARITY_PRICE_MULTIPLIER.get(rarity, 1.0)
        sell_price = int(base_price * multiplier * 0.5)
        
        rarity_emoji = RARITY_EMOJI.get(rarity, "⚪")
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"{rarity_emoji} {name} - {sell_price}💰",
                callback_data=f"shop_sell_item_{index}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="shop_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("shop_sell_item_"))
async def sell_item(callback: types.CallbackQuery):
    """Продає предмет"""
    try:
        item_index = int(callback.data.replace("shop_sell_item_", ""))
    except ValueError:
        await callback.answer("❌ Помилка!")
        return
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    if item_index < 0 or item_index >= len(player.inventory):
        await callback.answer("❌ Предмет не знайдено!")
        return
    
    item = player.inventory[item_index]
    
    if not isinstance(item, dict) or item.get("type") == "potion":
        await callback.answer("❌ Цей предмет не можна продати!")
        return
    
    # Розраховуємо ціну продажу
    base_price = item.get("base_price", 10)
    from src.config.equipment import RARITY_PRICE_MULTIPLIER
    rarity = item.get("rarity", "common")
    multiplier = RARITY_PRICE_MULTIPLIER.get(rarity, 1.0)
    sell_price = int(base_price * multiplier * 0.5)
    
    # Продаємо
    player.gold += sell_price
    item_name = item.get("name", "Предмет")
    player.inventory.pop(item_index)
    
    await db.save_player(player.to_dict())
    
    await callback.answer(f"✅ Продано {item_name} за {sell_price}💰!", show_alert=True)
    
    # Оновлюємо меню продажу
    await show_sell_menu(callback)