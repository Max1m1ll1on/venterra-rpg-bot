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


# ==================== ПЕРСОНАЖ ====================

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
    
    # Розраховуємо прогрес до наступного рівня
    exp_needed = player.get_required_experience()
    exp_progress = (player.experience / exp_needed * 100) if exp_needed > 0 else 100
    progress_bar = "█" * int(exp_progress / 10) + "░" * (10 - int(exp_progress / 10))
    
    # Формуємо повідомлення
    char_info = (
        f"👤 **{player.character_name}**\n"
        f"🏅 Клас: {CLASS_NAMES[player.character_class]}\n"
        f"⭐ Рівень: {player.level}\n\n"
        f"❤️ Здоров'я: {player.health}/{player.max_health}\n"
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
        f"💨 Шанс ухилення: {player.get_dodge_chance():.1f}%\n\n"
        f"🎯 Досвід: {player.experience}/{exp_needed}\n"
        f"{progress_bar} {exp_progress:.1f}%\n\n"
        f"📈 **Статистика:**\n"
        f"👹 Монстрів убито: {player.monsters_killed}\n"
        f"📋 Квестів виконано: {player.quests_completed}\n"
        f"💰 Всього заробили: {player.total_gold_earned}\n"
        f"⚔️ Завдано урону: {player.total_damage_dealt}\n"
        f"🩹 Отримано урону: {player.total_damage_taken}"
    )
    
    await message.answer(
        char_info,
        reply_markup=get_character_keyboard(),
        parse_mode="Markdown"
    )


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
    """Повертає гравця до міста через кнопку"""
    user_id = message.from_user.id
    
    # Перевіряємо чи гравець у бою
    from src.handlers.battle import active_battles
    if user_id in active_battles:
        await message.answer(
            "⚔️ **Ви в бою!**\n\n"
            "Неможливо покинути поле бою!\n"
            "Переможіть ворога або втечіть.",
            parse_mode="Markdown"
        )
        return
    
    # Регенеруємо здоров'я при поверненні
    db = Database()
    player_data = await db.get_player(user_id)
    
    if player_data:
        player = Player.from_dict(player_data)
        regen = player.regenerate_health(in_combat=False)
        await db.save_player(player.to_dict())
        
        await message.answer(
            f"🏰 **Ви повернулися до міста StaryFall**\n\n"
            f"Тут ви можете відпочити та підготуватися до нових пригод!\n\n"
            f"💚 Відновлено {regen} HP\n"
            f"❤️ Здоров'я: {player.health}/{player.max_health}",
            reply_markup=get_city_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "🏰 Ви повернулися до міста StaryFall.",
            reply_markup=get_city_keyboard()
        )