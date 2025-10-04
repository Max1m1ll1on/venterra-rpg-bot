# src/handlers/inventory.py - Оновлений обробник інвентаря

import logging
from aiogram import Router, F, types

from src.database import Database
from src.models.player import Player
from src.ui.keyboards import get_city_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "🎒 Інвентар")
async def show_inventory(message: types.Message):
    """Показує головне меню інвентаря"""
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if not player_data:
        await message.answer("❌ Персонаж не знайдено. Використайте /start")
        return
    
    player = Player.from_dict(player_data)
    
    inv_text = (
        f"🎒 **Інвентар**\n\n"
        f"👤 {player.character_name}\n"
        f"💰 Золото: {player.gold}\n"
        f"📦 Предметів: {len(player.inventory)}\n\n"
        f"Оберіть категорію:"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="⚔️ Спорядження", callback_data="inv_equipment"),
            types.InlineKeyboardButton(text="🧪 Зілля", callback_data="inv_potions")
        ],
        [
            types.InlineKeyboardButton(text="📦 Всі предмети", callback_data="inv_all")
        ]
    ])
    
    await message.answer(inv_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "inv_equipment")
async def show_equipment(callback: types.CallbackQuery):
    """Показує екіпірування"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка! Спробуйте ще раз.", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    equip_text = (
        f"⚔️ **Екіпірування**\n\n"
        f"{player.get_equipment_display()}\n\n"
        f"📊 **Характеристики:**\n"
        f"{player.get_total_stats_display()}\n\n"
        f"⚔️ Сила атаки: {player.get_attack_power()}\n"
        f"🛡️ Захист: {player.get_defense()}"
    )
    
    # Показуємо доступні предмети для екіпірування
    equipable_items = [
        item for item in player.inventory
        if isinstance(item, dict) and item.get("slot")
    ]
    
    keyboard_buttons = []
    
    if equipable_items:
        equip_text += f"\n\n📦 **Доступно для екіпірування:** {len(equipable_items)}"
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text="🔧 Одягнути предмет", 
                callback_data="inv_equip_list"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(
            text="👕 Зняти предмет", 
            callback_data="inv_unequip_list"
        )
    ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="inv_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(equip_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "inv_equip_list")
async def show_equip_list(callback: types.CallbackQuery):
    """Показує список предметів для екіпірування"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка! Спробуйте ще раз.", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    # Збираємо предмети для екіпірування з їх РЕАЛЬНИМИ індексами
    equipable_items = []
    for i, item in enumerate(player.inventory):
        if isinstance(item, dict) and item.get("slot"):
            equipable_items.append((i, item))
    
    if not equipable_items:
        await callback.answer("❌ Немає предметів для екіпірування!", show_alert=True)
        return
    
    try:
        from src.config.equipment import RARITY_EMOJI
    except ImportError:
        RARITY_EMOJI = {
            "common": "⚪", "uncommon": "🟢", "rare": "🔵",
            "epic": "🟣", "legendary": "🟠"
        }
    
    text = f"🔧 **Одягнути предмет**\n\n📦 Доступно: {len(equipable_items)}\n\n"
    keyboard_buttons = []
    
    # Групуємо по слотам
    slot_names = {
        "weapon": "⚔️", "head": "⛑️", "chest": "👕", "legs": "👖",
        "feet": "👢", "hands": "🧤", "offhand": "🛡️",
        "ring_1": "💍", "ring_2": "💍", "earring_1": "💎", 
        "earring_2": "💎", "amulet": "📿"
    }
    
    # ВАЖЛИВО: використовуємо РЕАЛЬНИЙ індекс з inventory!
    for real_index, item in equipable_items[:15]:  # Показуємо перші 15
        slot_emoji = slot_names.get(item.get("slot"), "📦")
        rarity_emoji = RARITY_EMOJI.get(item.get("rarity", "common"), "⚪")
        name = item.get("name", "Предмет")
        
        # Зберігаємо РЕАЛЬНИЙ індекс в callback_data
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"{slot_emoji} {rarity_emoji} {name}",
                callback_data=f"equip_real_{real_index}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="inv_equipment")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("equip_real_"))
async def equip_item(callback: types.CallbackQuery):
    """Екіпірує предмет"""
    try:
        # РЕАЛЬНИЙ індекс в inventory
        real_index = int(callback.data.replace("equip_real_", ""))
    except ValueError:
        await callback.answer("❌ Помилка!")
        return
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Перевіряємо індекс
    if real_index < 0 or real_index >= len(player.inventory):
        await callback.answer("❌ Предмет не знайдено!")
        return
    
    item = player.inventory[real_index]
    
    # Перевіряємо що це дійсно екіпірувальний предмет
    if not isinstance(item, dict) or not item.get("slot"):
        await callback.answer("❌ Цей предмет не можна екіпірувати!")
        return
    
    item_name = item.get("name", "Предмет")
    
    # Екіпіруємо
    success = player.equip_item(real_index)
    
    if success:
        await db.save_player(player.to_dict())
        await callback.answer(f"✅ {item_name} екіпіровано!")
        
        # Оновлюємо відображення
        await show_equipment(callback)
    else:
        await callback.answer("❌ Не вдалося екіпірувати предмет!", show_alert=True)


@router.callback_query(F.data == "inv_unequip_list")
async def show_unequip_list(callback: types.CallbackQuery):
    """Показує список екіпірованих предметів для зняття"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка! Спробуйте ще раз.", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    # Збираємо екіпіровані предмети
    equipped_items = []
    for slot, item in player.equipment.items():
        if item:
            equipped_items.append((slot, item))
    
    if not equipped_items:
        await callback.answer("❌ Немає екіпірованих предметів!", show_alert=True)
        return
    
    try:
        from src.config.equipment import RARITY_EMOJI
    except ImportError:
        RARITY_EMOJI = {
            "common": "⚪", "uncommon": "🟢", "rare": "🔵",
            "epic": "🟣", "legendary": "🟠"
        }
    
    text = f"👕 **Зняти предмет**\n\n⚔️ Екіпіровано: {len(equipped_items)}\n\n"
    keyboard_buttons = []
    
    slot_names = {
        "weapon": "⚔️ Зброя", "head": "⛑️ Шолом", "chest": "👕 Нагрудник",
        "legs": "👖 Набедреник", "feet": "👢 Взуття", "hands": "🧤 Рукавиці",
        "offhand": "🛡️ Щит", "ring_1": "💍 Перстень 1", "ring_2": "💍 Перстень 2",
        "earring_1": "💎 Сережка 1", "earring_2": "💎 Сережка 2", "amulet": "📿 Амулет"
    }
    
    for slot, item in equipped_items:
        slot_name = slot_names.get(slot, slot)
        rarity_emoji = RARITY_EMOJI.get(item.get("rarity", "common"), "⚪")
        item_name = item.get("name", "Предмет")
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"{slot_name}: {rarity_emoji} {item_name}",
                callback_data=f"unequip_slot_{slot}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="inv_equipment")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("unequip_slot_"))
async def unequip_item(callback: types.CallbackQuery):
    """Знімає предмет зі слоту"""
    slot = callback.data.replace("unequip_slot_", "")
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка! Спробуйте ще раз.", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    if slot not in player.equipment:
        await callback.answer("❌ Невірний слот!")
        return
    
    item = player.equipment.get(slot)
    if not item:
        await callback.answer("❌ Слот порожній!")
        return
    
    item_name = item.get("name", "Предмет")
    
    # Знімаємо
    success = player.unequip_item(slot)
    
    if success:
        await db.save_player(player.to_dict())
        await callback.answer(f"✅ {item_name} знято!")
        
        # Оновлюємо відображення
        await show_equipment(callback)
    else:
        await callback.answer("❌ Не вдалося зняти предмет!", show_alert=True)


@router.callback_query(F.data == "inv_potions")
async def show_potions(callback: types.CallbackQuery):
    """Показує зілля в інвентарі"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Збираємо зілля з РЕАЛЬНИМИ індексами
    potions = []
    for i, item in enumerate(player.inventory):
        if isinstance(item, dict) and item.get("type") == "potion":
            potions.append((i, item))
    
    if not potions:
        await callback.answer("❌ Немає зілля!", show_alert=True)
        return
    
    text = (
        f"🧪 **Зілля**\n\n"
        f"❤️ HP: {player.health}/{player.max_health}\n"
        f"📦 Зілля: {len(potions)}\n\n"
    )
    
    keyboard_buttons = []
    
    # ВАЖЛИВО: використовуємо РЕАЛЬНИЙ індекс!
    for real_index, potion in potions[:15]:  # Перші 15
        name = potion.get("name", "Зілля")
        effect_type = potion.get("effect_type", "")
        effect_value = potion.get("effect_value", 0)
        
        if effect_type == "heal":
            effect_text = f"+{effect_value} HP"
        elif effect_type == "full_heal":
            effect_text = "Повне відновлення"
        else:
            effect_text = ""
        
        # Зберігаємо РЕАЛЬНИЙ індекс
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"{name} ({effect_text})",
                callback_data=f"use_real_{real_index}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="inv_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("use_real_"))
async def use_potion(callback: types.CallbackQuery):
    """Використовує зілля"""
    try:
        real_index = int(callback.data.replace("use_real_", ""))
    except ValueError:
        await callback.answer("❌ Помилка!")
        return
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    if real_index < 0 or real_index >= len(player.inventory):
        await callback.answer("❌ Зілля не знайдено!")
        return
    
    potion = player.inventory[real_index]
    
    if not isinstance(potion, dict) or potion.get("type") != "potion":
        await callback.answer("❌ Це не зілля!")
        return
    
    potion_name = potion.get("name", "Зілля")
    effect_type = potion.get("effect_type", "")
    effect_value = potion.get("effect_value", 0)
    
    result_text = f"🧪 **Ви випили {potion_name}!**\n\n"
    
    # ЗІЛЛЯ ЗДОРОВ'Я
    if effect_type == "heal":
        if player.health >= player.max_health:
            await callback.answer("❤️ Ви вже на повному здоров'ї!", show_alert=True)
            return
        
        healed = player.heal(effect_value)
        result_text += f"❤️ Відновлено {healed} HP\n"
        result_text += f"❤️ Здоров'я: {player.health}/{player.max_health}"
        
    elif effect_type == "full_heal":
        if player.health >= player.max_health:
            await callback.answer("❤️ Ви вже на повному здоров'ї!", show_alert=True)
            return
        
        healed = player.max_health - player.health
        player.health = player.max_health
        result_text += f"✨ Повністю відновлено!\n"
        result_text += f"❤️ Здоров'я: {player.health}/{player.max_health}"
    
    # ✨ ЗІЛЛЯ МАНИ
    elif effect_type == "mana":
        if player.mana >= player.max_mana:
            await callback.answer("💙 Ви вже на повній мані!", show_alert=True)
            return
        
        mana_restored = int(player.max_mana * effect_value)
        mana_restored = min(mana_restored, player.max_mana - player.mana)
        player.mana += mana_restored
        
        result_text += f"💙 Відновлено {mana_restored} мани\n"
        result_text += f"💙 Мана: {player.mana}/{player.max_mana}"
    
    # БАФИ (не можна використати поза боєм)
    elif effect_type == "buff":
        await callback.answer("⚠️ Це зілля можна використати тільки перед боєм!", show_alert=True)
        return
    
    else:
        await callback.answer(f"❌ Невідомий тип зілля: {effect_type}!", show_alert=True)
        return
    
    # Видаляємо зілля
    player.inventory.pop(real_index)
    
    # Зберігаємо
    await db.save_player(player.to_dict())
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🧪 Ще зілля", callback_data="inv_potions")],
        [types.InlineKeyboardButton(text="🔙 До інвентаря", callback_data="inv_back")]
    ])
    
    await callback.message.edit_text(result_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer("✅ Зілля використано!")


@router.callback_query(F.data == "inv_all")
async def show_all_items(callback: types.CallbackQuery):
    """Показує всі предмети в інвентарі"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка! Спробуйте ще раз.", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    if not player.inventory:
        await callback.answer("❌ Інвентар порожній!", show_alert=True)
        return
    
    try:
        from src.config.equipment import RARITY_EMOJI
    except ImportError:
        RARITY_EMOJI = {
            "common": "⚪", "uncommon": "🟢", "rare": "🔵",
            "epic": "🟣", "legendary": "🟠"
        }
    
    text = f"📦 **Всі предмети** ({len(player.inventory)})\n\n"
    
    for i, item in enumerate(player.inventory[:20]):  # Перші 20
        if isinstance(item, dict):
            item_type = item.get("type", "item")
            name = item.get("name", "Предмет")
            rarity = item.get("rarity", "common")
            rarity_emoji = RARITY_EMOJI.get(rarity, "⚪")
            
            if item_type == "potion":
                text += f"🧪 {name}\n"
            elif item_type == "material":
                text += f"📦 {name}\n"
            else:
                text += f"{rarity_emoji} {name}\n"
        else:
            text += f"❓ {item}\n"
    
    if len(player.inventory) > 20:
        text += f"\n... та ще {len(player.inventory) - 20} предметів"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="inv_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "inv_back")
async def inventory_back(callback: types.CallbackQuery):
    """Повертає до головного меню інвентаря"""
    user_id = callback.from_user.id
    
    db = Database()
    player_data = await db.get_player(user_id)
    
    if not player_data:
        logger.error(f"Персонаж не знайдено для користувача {user_id}")
        await callback.answer("❌ Помилка! Персонаж не знайдено. Використайте /start", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    inv_text = (
        f"🎒 **Інвентар**\n\n"
        f"👤 {player.character_name}\n"
        f"💰 Золото: {player.gold}\n"
        f"📦 Предметів: {len(player.inventory)}\n\n"
        f"Оберіть категорію:"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="⚔️ Спорядження", callback_data="inv_equipment"),
            types.InlineKeyboardButton(text="🧪 Зілля", callback_data="inv_potions")
        ],
        [
            types.InlineKeyboardButton(text="📦 Всі предмети", callback_data="inv_all")
        ]
    ])
    
    await callback.message.edit_text(inv_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()