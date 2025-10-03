# src/handlers/guild.py - Обробник гільдії квестів

import logging
from aiogram import Router, F, types

from src.database import Database
from src.models.player import Player
from src.models.quest import Quest, QuestStatus
from src.config.quests import get_available_quests_for_level, get_quest_by_id
from src.ui.keyboards import get_city_keyboard

router = Router()
logger = logging.getLogger(__name__)


# ==================== ГОЛОВНЕ МЕНЮ ГІЛЬДІЇ ====================

@router.message(F.text == "🏰 Гільдія")
async def show_guild(message: types.Message):
    """Показує головне меню гільдії"""
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if not player_data:
        await message.answer("❌ Персонаж не знайдено. Використайте /start")
        return
    
    player = Player.from_dict(player_data)
    
    # Рахуємо активні та виконані квести
    active_quests = sum(1 for q in player.quests.values() if q.get("status") == "active")
    completed_quests = sum(1 for q in player.quests.values() if q.get("status") == "completed")
    
    guild_text = (
        f"🏰 **Гільдія Авантюристів**\n\n"
        f"Вітаємо, {player.character_name}!\n"
        f"⭐ Рівень: {player.level}\n"
        f"📋 Активних квестів: {active_quests}/3\n"
        f"✅ Виконаних квестів: {completed_quests}\n\n"
        f"Оберіть дію:"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📜 Взяти квест", callback_data="guild_take_quest")],
        [types.InlineKeyboardButton(text="✅ Здати квест", callback_data="guild_complete_quest")],
        [types.InlineKeyboardButton(text="📋 Мої квести", callback_data="guild_my_quests")],
        [types.InlineKeyboardButton(text="🚪 Вийти", callback_data="guild_exit")]
    ])
    
    await message.answer(guild_text, reply_markup=keyboard, parse_mode="Markdown")


# ==================== ВЗЯТИ КВЕСТ ====================

@router.callback_query(F.data == "guild_take_quest")
async def show_available_quests(callback: types.CallbackQuery):
    """Показує доступні квести"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Перевіряємо ліміт активних квестів
    active_count = sum(1 for q in player.quests.values() if q.get("status") == "active")
    if active_count >= 3:
        await callback.answer("❌ У вас вже 3 активних квести! Спочатку виконайте їх.", show_alert=True)
        return
    
    # Отримуємо доступні квести
    available_quests = get_available_quests_for_level(player.level)
    
    # Фільтруємо вже взяті
    available_quests = {
        qid: qdata for qid, qdata in available_quests.items()
        if qid not in player.quests or player.quests[qid].get("status") == "claimed"
    }
    
    if not available_quests:
        await callback.answer("❌ Немає доступних квестів для вашого рівня!", show_alert=True)
        return
    
    text = f"📜 **Доступні квести:**\n\n"
    keyboard_buttons = []
    
    for quest_id, quest_data in list(available_quests.items())[:5]:  # Показуємо перші 5
        name = quest_data["name"]
        level_req = quest_data["level_required"]
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"{name} (Рів.{level_req})",
                callback_data=f"guild_view_quest_{quest_id}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="guild_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("guild_view_quest_"))
async def view_quest_details(callback: types.CallbackQuery):
    """Показує деталі квесту"""
    quest_id = callback.data.replace("guild_view_quest_", "")
    quest_data = get_quest_by_id(quest_id)
    
    if not quest_data:
        await callback.answer("❌ Квест не знайдено!")
        return
    
    # Формуємо опис
    quest_type_names = {
        "kill": "Вбити ворогів",
        "survive": "Вижити у боях",
        "explore": "Дослідити",
        "collect": "Зібрати предмети"
    }
    
    quest_text = (
        f"{quest_data['name']}\n\n"
        f"📖 **Опис:**\n{quest_data['description']}\n\n"
        f"🎯 **Тип:** {quest_type_names.get(quest_data['type'], quest_data['type'])}\n"
        f"📊 **Ціль:** {quest_data['target']}\n"
        f"⭐ **Рівень:** {quest_data['level_required']}+\n\n"
        f"🎁 **Винагороди:**\n"
    )
    
    rewards = quest_data["rewards"]
    if "exp" in rewards:
        quest_text += f"✨ Досвід: +{rewards['exp']}\n"
    if "gold" in rewards:
        quest_text += f"💰 Золото: +{rewards['gold']}\n"
    if "item" in rewards:
        quest_text += f"📦 Предмет ({rewards['item']})\n"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Взяти квест", callback_data=f"guild_accept_{quest_id}")],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="guild_take_quest")]
    ])
    
    await callback.message.edit_text(quest_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("guild_accept_"))
async def accept_quest(callback: types.CallbackQuery):
    """Приймає квест"""
    quest_id = callback.data.replace("guild_accept_", "")
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Перевіряємо ліміт
    active_count = sum(1 for q in player.quests.values() if q.get("status") == "active")
    if active_count >= 3:
        await callback.answer("❌ У вас вже 3 активних квести!", show_alert=True)
        return
    
    # Отримуємо дані квесту
    quest_data = get_quest_by_id(quest_id)
    if not quest_data:
        await callback.answer("❌ Квест не знайдено!")
        return
    
    # Створюємо квест
    quest = Quest(quest_id, quest_data)
    quest.status = QuestStatus.ACTIVE
    
    # Додаємо до гравця
    player.quests[quest_id] = quest.to_dict()
    
    # Зберігаємо
    await db.save_player(player.to_dict())
    
    await callback.message.edit_text(
        f"✅ **Квест прийнято!**\n\n"
        f"{quest_data['name']}\n\n"
        f"Квест додано до вашого журналу.\n"
        f"Прогрес можна переглянути у 👤 Персонаж → 📋 Квести",
        parse_mode="Markdown"
    )
    
    await callback.answer("✅ Квест прийнято!")
    logger.info(f"Гравець {player.user_id} прийняв квест {quest_id}")


# ==================== ЗДАТИ КВЕСТ ====================

@router.callback_query(F.data == "guild_complete_quest")
async def show_completed_quests(callback: types.CallbackQuery):
    """Показує виконані квести"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Фільтруємо виконані квести
    completed = {
        qid: qdata for qid, qdata in player.quests.items()
        if qdata.get("status") == "completed"
    }
    
    if not completed:
        await callback.answer("❌ Немає виконаних квестів для здачі!", show_alert=True)
        return
    
    text = f"✅ **Виконані квести:**\n\n"
    keyboard_buttons = []
    
    for quest_id, quest_data in completed.items():
        name = quest_data["name"]
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"✅ {name}",
                callback_data=f"guild_claim_{quest_id}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="guild_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("guild_claim_"))
async def claim_quest_reward(callback: types.CallbackQuery):
    """Отримує винагороду за квест"""
    quest_id = callback.data.replace("guild_claim_", "")
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Перевіряємо чи квест виконано
    if quest_id not in player.quests:
        await callback.answer("❌ Квест не знайдено!")
        return
    
    quest_data = player.quests[quest_id]
    if quest_data.get("status") != "completed":
        await callback.answer("❌ Квест ще не виконано!")
        return
    
    # Отримуємо винагороди
    rewards = quest_data["rewards"]
    reward_text = f"🎉 **Квест виконано!**\n\n{quest_data['name']}\n\n🎁 **Винагороди:**\n"
    
    if "exp" in rewards:
        exp_result = player.add_experience(rewards["exp"])
        reward_text += f"✨ +{rewards['exp']} досвіду\n"
        if exp_result["leveled_up"]:
            reward_text += f"🎊 **НОВИЙ РІВЕНЬ {exp_result['new_level']}!**\n"
    
    if "gold" in rewards:
        player.add_gold(rewards["gold"])
        reward_text += f"💰 +{rewards['gold']} золота\n"
    
    if "item" in rewards:
        reward_text += f"📦 Отримано рідкісний предмет!\n"
    
    reward_text += f"\n💬 {rewards.get('message', 'Дякуємо за допомогу!')}"
    
    # Оновлюємо статус
    player.quests[quest_id]["status"] = "claimed"
    player.quests_completed += 1
    
    # Зберігаємо
    await db.save_player(player.to_dict())
    
    await callback.message.edit_text(reward_text, parse_mode="Markdown")
    await callback.answer("🎉 Винагорода отримана!")
    
    logger.info(f"Гравець {player.user_id} здав квест {quest_id}")


# ==================== МОЇ КВЕСТИ ====================

@router.callback_query(F.data == "guild_my_quests")
async def show_my_quests(callback: types.CallbackQuery):
    """Показує активні квести гравця"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Фільтруємо активні квести
    active = {
        qid: qdata for qid, qdata in player.quests.items()
        if qdata.get("status") == "active"
    }
    
    if not active:
        await callback.answer("❌ У вас немає активних квестів!", show_alert=True)
        return
    
    text = f"📋 **Мої квести:**\n\n"
    
    for quest_id, quest_data in active.items():
        name = quest_data["name"]
        progress = quest_data.get("progress", 0)
        target = quest_data.get("target", 1)
        
        # Прогрес-бар
        progress_percent = int((progress / target) * 10) if target > 0 else 0
        progress_bar = "█" * progress_percent + "░" * (10 - progress_percent)
        
        text += f"🔸 **{name}**\n"
        text += f"   {progress_bar} {progress}/{target}\n\n"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="guild_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


# ==================== НАВІГАЦІЯ ====================

@router.callback_query(F.data == "guild_back")
async def guild_back(callback: types.CallbackQuery):
    """Повертає до головного меню гільдії"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    active_quests = sum(1 for q in player.quests.values() if q.get("status") == "active")
    completed_quests = sum(1 for q in player.quests.values() if q.get("status") == "completed")
    
    guild_text = (
        f"🏰 **Гільдія Авантюристів**\n\n"
        f"Вітаємо, {player.character_name}!\n"
        f"⭐ Рівень: {player.level}\n"
        f"📋 Активних квестів: {active_quests}/3\n"
        f"✅ Виконаних квестів: {completed_quests}\n\n"
        f"Оберіть дію:"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📜 Взяти квест", callback_data="guild_take_quest")],
        [types.InlineKeyboardButton(text="✅ Здати квест", callback_data="guild_complete_quest")],
        [types.InlineKeyboardButton(text="📋 Мої квести", callback_data="guild_my_quests")],
        [types.InlineKeyboardButton(text="🚪 Вийти", callback_data="guild_exit")]
    ])
    
    await callback.message.edit_text(guild_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "guild_exit")
async def guild_exit(callback: types.CallbackQuery):
    """Виходить з гільдії"""
    await callback.message.delete()
    await callback.answer("До побачення!")