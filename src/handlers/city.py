# src/handlers/city.py - Обробники міста (ПОВНИЙ ВИПРАВЛЕНИЙ)

import logging
from aiogram import Router, F, types
from aiogram.filters import Command

from src.database import Database
from src.models.player import Player
from src.ui.keyboards import get_city_keyboard, get_character_keyboard
from src.config.constants import CLASS_NAMES
from src.config.settings import settings

router = Router()
logger = logging.getLogger(__name__)


# Замініть обробники у src/handlers/city.py
# Використовуємо існуючі callback'и з keyboards.py: char_stats, char_quests, char_achievements

@router.message(F.text == "👤 Персонаж")
async def show_character(message: types.Message):
    """Показує інформацію про персонажа"""
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if not player_data:
        await message.answer(
            "❌ Персонаж не знайдено. Використайте /start для створення."
        )
        return
    
    # Перевіряємо чи в бою
    from src.handlers.battle import active_battles
    in_battle = message.from_user.id in active_battles
    
    if in_battle:
        await message.answer(
            "⚔️ **Ви в бою!**\n\n"
            "Зосередьтесь на битві!",
            parse_mode="Markdown"
        )
        return
    
    player = Player.from_dict(player_data)
    
    # ✨ НОВЕ: Застосовуємо офлайн регенерацію
    regen_result = player.apply_offline_regeneration()
    
    # Зберігаємо оновлений стан
    if regen_result["hp"] > 0 or regen_result["mana"] > 0:
        await db.save_player(player.to_dict())
    
    # Розраховуємо прогрес до наступного рівня
    exp_needed = player.get_required_experience()
    exp_progress = (player.experience / exp_needed * 100) if exp_needed > 0 else 100
    progress_bar = "█" * int(exp_progress / 10) + "░" * (10 - int(exp_progress / 10))
    
    # Формуємо повідомлення
    char_info = (
        f"👤 **{player.character_name}**\n"
        f"🏅 Клас: {CLASS_NAMES[player.character_class]}\n"
        f"⭐ Рівень: {player.level}\n\n"
    )
    
    # ✨ НОВЕ: Показуємо повідомлення про регенерацію
    if regen_result["hp"] > 0 or regen_result["mana"] > 0:
        offline_minutes = regen_result["offline_time"] // 60
        char_info += f"💤 Ви відпочивали {offline_minutes} хв\n"
        if regen_result["hp"] > 0:
            char_info += f"💚 Відновлено {regen_result['hp']} HP\n"
        if regen_result["mana"] > 0:
            char_info += f"💙 Відновлено {regen_result['mana']} мани\n"
        char_info += "\n"
    
    char_info += (
        f"❤️ Здоров'я: {player.health}/{player.max_health}\n"
        f"💙 Мана: {player.mana}/{player.max_mana}\n"
        f"💰 Золото: {player.gold}\n\n"
        f"📊 **Характеристики:**\n"
        f"💪 Сила: {player.strength}\n"
        f"🏃 Спритність: {player.agility}\n"
        f"🧠 Інтелект: {player.intelligence}\n"
        f"🛡️ Витривалість: {player.stamina}\n"
        f"🎭 Харизма: {player.charisma}\n"
    )
    
    if player.free_points > 0:
        char_info += f"\n✨ Вільних очок: {player.free_points}\n"
    
    char_info += (
        f"\n⚔️ Бонус атаки: +{player.get_attack_bonus()}\n"
        f"🛡️ Клас броні (AC): {player.get_armor_class()}\n"
        f"🗡️ Захист: {player.get_defense()}\n"
        f"💨 Шанс ухилення: {player.get_dodge_chance():.1f}%\n\n"
        f"🎯 Досвід: {player.experience}/{exp_needed}\n"
        f"{progress_bar} {exp_progress:.1f}%"
    )
    
    await message.answer(
        char_info,
        reply_markup=get_character_keyboard(),
        parse_mode="Markdown"
    )


# ==================== СТАТИСТИКА ====================

@router.callback_query(F.data == "char_stats")
async def show_character_stats(callback: types.CallbackQuery):
    """Показує детальну статистику персонажа"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка!", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    # Розраховуємо додаткові дані
    total_battles = player.monsters_killed
    avg_damage_dealt = int(player.total_damage_dealt / total_battles) if total_battles > 0 else 0
    avg_damage_taken = int(player.total_damage_taken / total_battles) if total_battles > 0 else 0
    
    stats_text = (
        f"📊 **Статистика {player.character_name}**\n\n"
        f"⚔️ **Бойова статистика:**\n"
        f"👹 Монстрів убито: {player.monsters_killed}\n"
        f"⚔️ Всього завдано урону: {player.total_damage_dealt}\n"
        f"🩹 Всього отримано урону: {player.total_damage_taken}\n"
        f"📈 Середній урон за бій: {avg_damage_dealt}\n"
        f"📉 Середній урон отримано: {avg_damage_taken}\n\n"
        f"💰 **Економіка:**\n"
        f"💰 Поточне золото: {player.gold}\n"
        f"💎 Всього заробили: {player.total_gold_earned}\n"
        f"💸 Всього витрачено: {player.total_gold_earned - player.gold}\n\n"
        f"📋 **Прогресія:**\n"
        f"⭐ Рівень: {player.level}\n"
        f"🎯 Досвід: {player.experience}/{player.get_required_experience()}\n"
        f"📜 Квестів виконано: {player.quests_completed}\n"
        f"🏆 Досягнень: {len(player.achievements)}"
    )
    
    # Кнопка назад
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 Назад до персонажа", callback_data="char_back")]
    ])
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== КВЕСТИ ====================

@router.callback_query(F.data == "char_quests")
async def show_character_quests(callback: types.CallbackQuery):
    """Показує активні квести персонажа"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка!", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    # Перевіряємо наявність квестів
    if not player.quests or len(player.quests) == 0:
        quests_text = (
            f"🎯 **Квести {player.character_name}**\n\n"
            f"У вас немає активних квестів.\n\n"
            f"💡 Відвідайте 🏰 Гільдію для отримання квестів!"
        )
    else:
        quests_text = f"🎯 **Активні квести:**\n\n"
        
        for quest_id, quest_data in player.quests.items():
            if quest_data.get("status") == "active":
                quest_name = quest_data.get("name", "Невідомий квест")
                progress = quest_data.get("progress", 0)
                target = quest_data.get("target", 1)
                
                # Прогрес-бар для квесту
                quest_progress = int((progress / target) * 10) if target > 0 else 0
                quest_bar = "█" * quest_progress + "░" * (10 - quest_progress)
                
                quests_text += f"🔸 **{quest_name}**\n"
                quests_text += f"   {quest_bar} {progress}/{target}\n\n"
        
        if "🔸" not in quests_text:
            quests_text += "Всі квести виконано! Поверніться до гільдії.\n"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 Назад до персонажа", callback_data="char_back")]
    ])
    
    await callback.message.edit_text(
        quests_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== ДОСЯГНЕННЯ ====================

@router.callback_query(F.data == "char_achievements")
async def show_character_achievements(callback: types.CallbackQuery):
    """Показує досягнення персонажа"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка!", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    if not player.achievements or len(player.achievements) == 0:
        achievements_text = (
            f"🏆 **Досягнення {player.character_name}**\n\n"
            f"У вас поки немає досягнень.\n\n"
            f"💡 Продовжуйте грати щоб розблокувати досягнення!"
        )
    else:
        achievements_text = f"🏆 **Ваші досягнення:**\n\n"
        
        for achievement in player.achievements:
            achievement_name = achievement.get("name", "Досягнення")
            achievement_desc = achievement.get("description", "")
            
            achievements_text += f"🏅 **{achievement_name}**\n"
            achievements_text += f"   {achievement_desc}\n\n"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 Назад до персонажа", callback_data="char_back")]
    ])
    
    await callback.message.edit_text(
        achievements_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== ПОВЕРНЕННЯ ====================

@router.callback_query(F.data == "char_back")
async def character_back(callback: types.CallbackQuery):
    """Повертає до головного меню персонажа"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    
    if not player_data:
        await callback.answer("❌ Помилка!", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    
    exp_needed = player.get_required_experience()
    exp_progress = (player.experience / exp_needed * 100) if exp_needed > 0 else 100
    progress_bar = "█" * int(exp_progress / 10) + "░" * (10 - int(exp_progress / 10))
    
    char_info = (
        f"👤 **{player.character_name}**\n"
        f"🏅 Клас: {CLASS_NAMES[player.character_class]}\n"
        f"⭐ Рівень: {player.level}\n\n"
        f"❤️ Здоров'я: {player.health}/{player.max_health}\n"
        f"💙 Мана: {player.mana}/{player.max_mana}\n"
        f"💰 Золото: {player.gold}\n\n"
        f"📊 **Характеристики:**\n"
        f"💪 Сила: {player.strength}\n"
        f"🏃 Спритність: {player.agility}\n"
        f"🧠 Інтелект: {player.intelligence}\n"
        f"🛡️ Витривалість: {player.stamina}\n"
        f"🎭 Харизма: {player.charisma}\n"
    )
    
    if player.free_points > 0:
        char_info += f"\n✨ Вільних очок: {player.free_points}\n"
    
    char_info += (
        f"\n⚔️ Сила атаки: {player.get_attack_power()}\n"
        f"🛡️ Захист: {player.get_defense()}\n"
        f"🎯 AC (Armor Class): {player.get_armor_class()}\n"
        f"💨 Шанс ухилення: {player.get_dodge_chance():.1f}%\n\n"
        f"🎯 Досвід: {player.experience}/{exp_needed}\n"
        f"{progress_bar} {exp_progress:.1f}%"
    )
    
    await callback.message.edit_text(
        char_info,
        reply_markup=get_character_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== ЛІКАР ====================

@router.message(F.text == "⚕️ Лікар")
async def show_healer(message: types.Message):
    """Показує лікаря"""
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if not player_data:
        await message.answer(
            "❌ Персонаж не знайдено. Використайте /start для створення."
        )
        return
    
    player = Player.from_dict(player_data)
    heal_cost = settings.HEAL_COST
    
    # Перевіряємо чи потрібне лікування
    if player.health >= player.max_health:
        await message.answer(
            "⚕️ **Лікар StaryFall**\n\n"
            "❤️ Ви вже повністю здорові!\n"
            "Повертайтесь, коли потребуватимете лікування.\n\n"
            f"💰 Вартість лікування: {heal_cost} золота",
            parse_mode="Markdown"
        )
        return
    
    # Показуємо інформацію
    hp_missing = player.max_health - player.health
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text=f"❤️ Лікуватися ({heal_cost} 💰)",
            callback_data="heal_player"
        )],
        [types.InlineKeyboardButton(
            text="🚪 Вийти",
            callback_data="leave_healer"
        )]
    ])
    
    await message.answer(
        f"⚕️ **Лікар StaryFall**\n\n"
        f"Доброго дня, {player.character_name}!\n"
        f"Я бачу ви поранені. Дозвольте мені допомогти.\n\n"
        f"❤️ Ваше здоров'я: {player.health}/{player.max_health}\n"
        f"🩹 Відновлю: {hp_missing} HP\n"
        f"💰 Вартість: {heal_cost} золота\n\n"
        f"💰 У вас: {player.gold} золота",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "heal_player")
async def heal_player(callback: types.CallbackQuery):
    """Лікує персонажа"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    heal_cost = settings.HEAL_COST
    
    # Перевіряємо золото
    if player.gold < heal_cost:
        await callback.answer(
            f"❌ Недостатньо золота! Потрібно {heal_cost}, у вас {player.gold}",
            show_alert=True
        )
        return
    
    # Перевіряємо чи потрібне лікування
    if player.health >= player.max_health:
        await callback.answer("❤️ Ви вже здорові!", show_alert=True)
        return
    
    # Лікуємо
    hp_restored = player.max_health - player.health
    player.health = player.max_health
    player.gold -= heal_cost
    
    # Зберігаємо
    await db.save_player(player.to_dict())
    
    await callback.message.edit_text(
        f"✅ **Лікування завершено!**\n\n"
        f"❤️ Відновлено: {hp_restored} HP\n"
        f"💰 Сплачено: {heal_cost} золота\n"
        f"💰 Залишилось: {player.gold} золота\n\n"
        f"❤️ Здоров'я: {player.health}/{player.max_health}\n\n"
        f"Бережіть себе у пригодах!",
        parse_mode="Markdown"
    )
    
    await callback.answer("✅ Ви зцілені!")
    logger.info(f"Гравець {player.user_id} ({player.character_name}) вилікувався")


@router.callback_query(F.data == "leave_healer")
async def leave_healer(callback: types.CallbackQuery):
    """Виходить від лікаря"""
    await callback.message.delete()
    await callback.answer()


# ==================== ХРАМ ====================

@router.message(F.text == "⛪ Храм")
async def show_temple(message: types.Message):
    """Показує храм для покращення характеристик"""
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if not player_data:
        await message.answer(
            "❌ Персонаж не знайдено. Використайте /start для створення."
        )
        return
    
    player = Player.from_dict(player_data)
    
    # Розраховуємо вартість покращення
    upgrade_cost = int(settings.TEMPLE_UPGRADE_BASE_COST * (1.1 ** (player.level - 1)))
    
    temple_text = (
        f"⛪ **Храм Світла**\n\n"
        f"Вітаю у святилищі, {player.character_name}.\n"
        f"Тут ви можете покращити свої характеристики.\n\n"
        f"📊 **Ваші характеристики:**\n"
        f"💪 Сила: {player.strength}\n"
        f"🏃 Спритність: {player.agility}\n"
        f"🧠 Інтелект: {player.intelligence}\n"
        f"🛡️ Витривалість: {player.stamina}\n"
        f"🎭 Харизма: {player.charisma}\n\n"
        f"✨ Вільних очок: {player.free_points}\n"
        f"💰 Ваше золото: {player.gold}\n\n"
    )
    
    if player.free_points > 0:
        temple_text += (
            f"💡 **Для покращення потрібно:**\n"
            f"• 1 вільне очко характеристики\n"
            f"• {upgrade_cost} золота\n\n"
            f"Оберіть характеристику для покращення:"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=f"💪 Сила (+1)",
                    callback_data="upgrade_strength"
                ),
                types.InlineKeyboardButton(
                    text=f"🏃 Спритність (+1)",
                    callback_data="upgrade_agility"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=f"🧠 Інтелект (+1)",
                    callback_data="upgrade_intelligence"
                ),
                types.InlineKeyboardButton(
                    text=f"🛡️ Витривалість (+1)",
                    callback_data="upgrade_stamina"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=f"🎭 Харизма (+1)",
                    callback_data="upgrade_charisma"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🚪 Вийти",
                    callback_data="leave_temple"
                )
            ]
        ])
    else:
        temple_text += (
            f"❌ У вас немає вільних очок характеристик.\n"
            f"Підвищуйте рівень, щоб отримати більше очок!"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="🚪 Вийти",
                callback_data="leave_temple"
            )]
        ])
    
    await message.answer(
        temple_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("upgrade_"))
async def upgrade_stat(callback: types.CallbackQuery):
    """Покращує характеристику"""
    stat_name = callback.data.replace("upgrade_", "")
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Розраховуємо вартість
    upgrade_cost = int(settings.TEMPLE_UPGRADE_BASE_COST * (1.1 ** (player.level - 1)))
    
    # Перевірки
    if player.free_points < 1:
        await callback.answer(
            "❌ Недостатньо вільних очок!",
            show_alert=True
        )
        return
    
    if player.gold < upgrade_cost:
        await callback.answer(
            f"❌ Недостатньо золота! Потрібно {upgrade_cost}, у вас {player.gold}",
            show_alert=True
        )
        return
    
    # Покращуємо характеристику
    old_value = getattr(player, stat_name)
    success = player.add_stat(stat_name)
    
    if not success:
        await callback.answer("❌ Помилка покращення!", show_alert=True)
        return
    
    # Списуємо золото
    player.gold -= upgrade_cost
    
    # Зберігаємо
    await db.save_player(player.to_dict())
    
    # Назви характеристик
    stat_names_ua = {
        "strength": "💪 Силу",
        "agility": "🏃 Спритність",
        "intelligence": "🧠 Інтелект",
        "stamina": "🛡️ Витривалість",
        "charisma": "🎭 Харизму"
    }
    
    stat_display = stat_names_ua.get(stat_name, stat_name)
    new_value = getattr(player, stat_name)
    
    result_text = (
        f"✅ **Характеристику покращено!**\n\n"
        f"{stat_display}: {old_value} → {new_value}\n\n"
        f"💰 Витрачено: {upgrade_cost} золота\n"
        f"💰 Залишилось: {player.gold} золота\n"
        f"✨ Вільних очок: {player.free_points}"
    )
    
    if stat_name == "stamina":
        result_text += f"\n\n❤️ Макс. здоров'я: {player.max_health}"
    
    await callback.message.edit_text(
        result_text,
        parse_mode="Markdown"
    )
    
    await callback.answer(f"✅ {stat_display} покращено!")
    logger.info(f"Гравець {player.user_id} покращив {stat_name}: {old_value} → {new_value}")


@router.callback_query(F.data == "leave_temple")
async def leave_temple(callback: types.CallbackQuery):
    """Виходить з храму"""
    await callback.message.delete()
    await callback.answer()


# ==================== КНОПКИ ПРИГОД ====================

@router.message(F.text == "🗺️ Досліджувати")
async def explore_world(message: types.Message):
    """Показує меню досліджень"""
    user_id = message.from_user.id
    
    # Перевіряємо чи гравець у бою
    from src.handlers.battle import active_battles
    if user_id in active_battles:
        await message.answer(
            "⚔️ **Ви в бою!**\n\n"
            "Спочатку завершіть поточну битву!",
            parse_mode="Markdown"
        )
        return
    
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if not player_data:
        await message.answer("❌ Персонаж не знайдено.")
        return
    
    player = Player.from_dict(player_data)
    
    if player.health <= 0:
        await message.answer(
            "💀 **Ви занадто ослаблені!**\n\n"
            "Поверніться до міста та відвідайте лікаря.",
            parse_mode="Markdown"
        )
        return
    
    from src.ui.keyboards import get_adventures_keyboard
    
    adventures_text = (
        f"🗺️ **Дослідження світу**\n\n"
        f"👤 {player.character_name} (Рів. {player.level})\n"
        f"❤️ HP: {player.health}/{player.max_health}\n"
        f"⚔️ Атака: {player.get_attack_power()}\n\n"
        f"Оберіть локацію:"
    )
    
    await message.answer(
        adventures_text,
        reply_markup=get_adventures_keyboard(player.level),
        parse_mode="Markdown"
    )


@router.message(F.text == "🏰 Повернутися до міста")
async def return_to_city_button(message: types.Message):
    """Повернення до міста через кнопку"""
    user_id = message.from_user.id
    
    # Перевіряємо чи не в бою
    from src.handlers.battle import active_battles
    if user_id in active_battles:
        await message.answer(
            "⚔️ **Ви в бою!**\n\n"
            "Неможливо покинути поле бою!\n"
            "Переможіть ворога або втечіть.",
            parse_mode="Markdown"
        )
        return
    
    # ✨ ВИПРАВЛЕНО: Застосовуємо офлайн регенерацію (на основі часу)
    db = Database()
    player_data = await db.get_player(user_id)
    
    if player_data:
        player = Player.from_dict(player_data)
        
        # Застосовуємо регенерацію на основі ЧАСУ
        regen_result = player.apply_offline_regeneration()
        
        # Зберігаємо
        await db.save_player(player.to_dict())
        
        # Формуємо повідомлення
        city_text = f"🏰 **Ви повернулися до міста StaryFall**\n\n"
        
        # Показуємо регенерацію тільки якщо вона була
        if regen_result["hp"] > 0 or regen_result["mana"] > 0:
            city_text += "💤 Під час відпочинку:\n"
            if regen_result["hp"] > 0:
                city_text += f"💚 Відновлено {regen_result['hp']} HP\n"
            if regen_result["mana"] > 0:
                city_text += f"💙 Відновлено {regen_result['mana']} мани\n"
            city_text += "\n"
        
        city_text += (
            f"Тут ви можете відпочити та підготуватися до нових пригод!\n\n"
            f"❤️ Здоров'я: {player.health}/{player.max_health}\n"
            f"💙 Мана: {player.mana}/{player.max_mana}"
        )
        
        await message.answer(
            city_text,
            reply_markup=get_city_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "🏰 Ви повернулися до міста StaryFall.",
            reply_markup=get_city_keyboard()
        )