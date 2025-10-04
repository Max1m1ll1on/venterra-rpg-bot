# src/handlers/tavern.py - Таверна

import logging
from aiogram import Router, F, types

from src.database import Database
from src.models.player import Player

router = Router()
logger = logging.getLogger(__name__)

# ============================================================
# КРОК 1: Додати зілля мани в src/handlers/tavern.py
# ============================================================
# Знайдіть словник TAVERN_POTIONS і додайте ДО НЬОГО ці 3 зілля:

TAVERN_POTIONS = {
    "health_potion": {
        "name": "❤️ Зілля здоров'я",
        "price": 30,
        "type": "potion",
        "effect_type": "heal",
        "effect_value": 50,
        "description": "Відновлює 50 HP"
    },
    "mega_health": {
        "name": "❤️‍🔥 Велике зілля здоров'я",
        "price": 60,
        "type": "potion",
        "effect_type": "heal",
        "effect_value": 100,
        "description": "Відновлює 100 HP"
    },
    "strength_potion": {
        "name": "⚡ Зілля сили",
        "price": 50,
        "type": "potion",
        "effect_type": "buff",
        "effect_stat": "strength",
        "effect_value": 3,
        "description": "+3 до Сили на наступний бій"
    },
    "agility_potion": {
        "name": "💨 Зілля спритності",
        "price": 50,
        "type": "potion",
        "effect_type": "buff",
        "effect_stat": "agility",
        "effect_value": 3,
        "description": "+3 до Спритності на наступний бій"
    },
    "defense_potion": {
        "name": "🛡️ Зілля захисту",
        "price": 45,
        "type": "potion",
        "effect_type": "buff",
        "effect_stat": "stamina",
        "effect_value": 2,
        "description": "+2 до Витривалості на наступний бій"
    },
    "ale": {
        "name": "🍺 Кухоль елю",
        "price": 10,
        "type": "potion",
        "effect_type": "heal",
        "effect_value": 20,
        "description": "Відновлює 20 HP"
    },
    "elixir": {
        "name": "✨ Еліксир героя",
        "price": 100,
        "type": "potion",
        "effect_type": "full_heal",
        "effect_value": 0,
        "description": "Повністю відновлює HP"
    },
    
    # ✨ НОВІ ЗІЛЛЯ МАНИ - ДОДАЙТЕ ЦІ 3 РЯДКИ:
    "small_mana": {
        "name": "💙 Мале зілля мани",
        "price": 30,
        "type": "potion",
        "effect_type": "mana",
        "effect_value": 0.25,  # 25% мани
        "description": "Відновлює 25% мани"
    },
    "medium_mana": {
        "name": "💙 Середнє зілля мани",
        "price": 60,
        "type": "potion",
        "effect_type": "mana",
        "effect_value": 0.5,  # 50% мани
        "description": "Відновлює 50% мани"
    },
    "large_mana": {
        "name": "💙 Велике зілля мани",
        "price": 100,
        "type": "potion",
        "effect_type": "mana",
        "effect_value": 1.0,  # 100% мани
        "description": "Повністю відновлює ману"
    }
}


# ==================== ГОЛОВНЕ МЕНЮ ТАВЕРНИ ====================

@router.message(F.text == "🍺 Таверна")
async def show_tavern(message: types.Message):
    """Показує головне меню таверни"""
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if not player_data:
        await message.answer(
            "❌ Персонаж не знайдено. Використайте /start для створення."
        )
        return
    
    player = Player.from_dict(player_data)
    
    tavern_text = (
        f"🍺 **Таверна 'Гордість Вентерри'**\n\n"
        f"Ви заходите в затишну таверну. Пахне елем, смаженим м'ясом "
        f"та пригодами!\n\n"
        f"За стійкою бармен Торгрім наливає пінисте пиво, а в кутку "
        f"бард грає веселу пісню.\n\n"
        f"👤 {player.character_name}\n"
        f"💰 Золото: {player.gold}\n"
        f"❤️ HP: {player.health}/{player.max_health}\n\n"
        f"🍺 Що бажаєте?"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="🧪 Купити зілля",
            callback_data="tavern_potions"
        )],
        [types.InlineKeyboardButton(
            text="💬 Поговорити з бардом",
            callback_data="tavern_bard"
        )],
        [types.InlineKeyboardButton(
            text="👥 Вступити у чат",
            url="https://t.me/venterra_chat"
        )],
        [types.InlineKeyboardButton(
            text="🎲 Зіграти в кості",
            callback_data="tavern_dice_game"
        )],
        [types.InlineKeyboardButton(
            text="🚪 Вийти",
            callback_data="tavern_exit"
        )]
    ])
    
    await message.answer(
        tavern_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# Альтернативний обробник для callback (якщо викликається з іншого місця)
@router.callback_query(F.data == "show_tavern")
async def show_tavern_callback(callback: types.CallbackQuery):
    """Показує таверну через callback"""
    await show_tavern(callback.message)
    await callback.answer()


# ==================== КУПІВЛЯ ЗІЛЛЬ ====================

@router.callback_query(F.data == "tavern_potions")
async def show_potions(callback: types.CallbackQuery):
    """Показує асортимент зілль"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    potions_text = (
        f"🧪 **Зілля таверни**\n\n"
        f"Торгрім показує вам свою колекцію:\n\n"
        f"💰 Ваше золото: {player.gold}\n\n"
        f"📜 Асортимент:"
    )
    
    # Створюємо кнопки для кожного зілля
    keyboard_buttons = []
    for potion_id, potion in TAVERN_POTIONS.items():
        can_afford = player.gold >= potion["price"]
        emoji = "✅" if can_afford else "❌"
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"{emoji} {potion['name']} - {potion['price']} 💰",
                callback_data=f"tavern_view_{potion_id}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(
            text="🔙 До таверни",
            callback_data="tavern_back"
        )
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(
        potions_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== ПЕРЕГЛЯД ЗІЛЛЯ ====================

@router.callback_query(F.data.startswith("tavern_view_"))
async def view_potion(callback: types.CallbackQuery):
    """Показує детальну інформацію про зілля"""
    potion_id = callback.data.replace("tavern_view_", "")
    
    if potion_id not in TAVERN_POTIONS:
        await callback.answer("❌ Зілля не знайдено!")
        return
    
    potion = TAVERN_POTIONS[potion_id]
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Формуємо опис
    potion_text = (
        f"🧪 **{potion['name']}**\n\n"
        f"💰 Ціна: **{potion['price']} золота**\n\n"
        f"📖 Опис: {potion['description']}\n\n"
    )
    
    # Додаємо ефект
    if potion['effect_type'] == 'heal':
        potion_text += f"💊 Відновлює {potion['effect_value']} HP\n"
    elif potion['effect_type'] == 'full_heal':
        potion_text += f"✨ Повністю відновлює здоров'я!\n"
    elif potion['effect_type'] == 'buff':
        stat_names = {
            'strength': '💪 Силу',
            'agility': '🏃 Спритність',
            'stamina': '🛡️ Витривалість',
            'intelligence': '🧠 Інтелект'
        }
        stat = stat_names.get(potion['effect_stat'], potion['effect_stat'])
        potion_text += f"⚡ Підвищує {stat} на {potion['effect_value']} у наступному бою!\n"
    
    potion_text += f"\n💰 У вас: {player.gold} золота"
    
    # Кнопки
    can_afford = player.gold >= potion["price"]
    
    keyboard_buttons = []
    if can_afford:
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text="✅ Купити",
                callback_data=f"tavern_buy_{potion_id}"
            )
        ])
    else:
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text="❌ Недостатньо золота",
                callback_data="tavern_no_money"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(
            text="🔙 До зілль",
            callback_data="tavern_potions"
        )
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(
        potion_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== КУПІВЛЯ ====================

@router.callback_query(F.data.startswith("tavern_buy_"))
async def buy_potion(callback: types.CallbackQuery):
    """Купує зілля"""
    potion_id = callback.data.replace("tavern_buy_", "")
    
    if potion_id not in TAVERN_POTIONS:
        await callback.answer("❌ Зілля не знайдено!")
        return
    
    potion = TAVERN_POTIONS[potion_id]
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Перевіряємо золото
    if player.gold < potion["price"]:
        await callback.answer(
            f"❌ Недостатньо золота! Потрібно {potion['price']}, у вас {player.gold}",
            show_alert=True
        )
        return
    
    # Купуємо
    player.gold -= potion["price"]
    
    # Створюємо предмет для інвентаря
    potion_item = {
        "name": potion["name"],
        "type": potion["type"],
        "effect_type": potion["effect_type"],
        "effect_value": potion["effect_value"],
        "description": potion["description"]
    }
    
    # Додаємо спеціальні поля для бафів
    if potion["effect_type"] == "buff":
        potion_item["effect_stat"] = potion["effect_stat"]
    
    player.inventory.append(potion_item)
    
    # Зберігаємо
    await db.save_player(player.to_dict())
    
    success_text = (
        f"✅ **Покупка завершена!**\n\n"
        f"🧪 Ви купили: {potion['name']}\n"
        f"💰 Заплачено: {potion['price']} золота\n"
        f"💰 Залишилось: {player.gold} золота\n\n"
        f"📦 Зілля додано до інвентаря!\n\n"
        f"💡 Використайте його під час бою або вилікуйтесь зараз."
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="🧪 Купити ще",
                callback_data="tavern_potions"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🍺 До таверни",
                callback_data="tavern_back"
            )
        ]
    ])
    
    await callback.message.edit_text(
        success_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer("✅ Куплено!")
    
    logger.info(f"Гравець {player.user_id} купив {potion['name']} у таверні за {potion['price']} золота")


# ==================== БАРД ====================

@router.callback_query(F.data == "tavern_bard")
async def talk_to_bard(callback: types.CallbackQuery):
    """Розмова з бардом"""
    import random
    import time
    
    stories = [
        (
            "🎵 **Пісня про Драконобійцю**\n\n"
            "Бард співає про легендарного героя, який переміг Чорного Дракона "
            "у печерах Мор'Кату. Кажуть, його меч досі там...\n\n"
            "💡 Підказка: Досліджуйте печери на високих рівнях!"
        ),
        (
            "📖 **Казка про Забуте Місто**\n\n"
            "Бард розповідає про стародавнє місто, сховане в горах. "
            "Там схована неймовірна скарбниця, але стережуть її страшні привиди...\n\n"
            "💡 Підказка: Руїни повні таємниць!"
        ),
        (
            "🗡️ **Легенда про Меч Світла**\n\n"
            "Десь у світі існує легендарний Меч Світла, який дає величезну силу. "
            "Його може здобути лише найдостойніший воїн.\n\n"
            "💡 Підказка: Виконуйте квести у гільдії!"
        ),
        (
            "🍺 **Історія про Торгріма**\n\n"
            "Бард розповідає, що Торгрім, бармен цієї таверни, колись був "
            "найсильнішим воїном у королівстві. Але одного дня він залишив меч "
            "і відкрив таверну. Ніхто не знає чому...\n\n"
            "🤔 Таємниця залишається таємницею..."
        ),
        (
            "⚔️ **Баллада про Героїв Вентерри**\n\n"
            "Бард співає про відважних героїв, які колись рятували цей світ. "
            "Можливо, ви станете одним з них?\n\n"
            "✨ Продовжуйте свій шлях, герою!"
        ),
        (
            "🌙 **Легенда про Місячний Камінь**\n\n"
            "За переказами, десь у болотах лежить Місячний Камінь, "
            "який дарує неймовірну силу. Але знайти його дуже важко...\n\n"
            "💡 Підказка: Досліджуйте болота!"
        )
    ]
    
    # ✨ ВИПРАВЛЕННЯ: Додаємо timestamp щоб кожне повідомлення було унікальним
    story = random.choice(stories)
    timestamp = int(time.time())
    
    # Додаємо невидимий символ з timestamp щоб текст завжди був різним
    story_with_timestamp = f"{story}\n\n🕐 _(Оповідь #{timestamp})_"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="🎵 Послухати ще",
            callback_data="tavern_bard"
        )],
        [types.InlineKeyboardButton(
            text="🍺 До таверни",
            callback_data="tavern_back"
        )]
    ])
    
    # ✨ ДОДАТКОВО: Обробка помилки якщо все ж таки текст ідентичний
    try:
        await callback.message.edit_text(
            story_with_timestamp,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()
    except Exception as e:
        # Якщо помилка "message is not modified" - просто ігноруємо
        if "message is not modified" in str(e):
            await callback.answer("🎵 Бард повторює історію...")
        else:
            # Інші помилки - логуємо
            logger.error(f"Помилка в talk_to_bard: {e}")
            await callback.answer("❌ Помилка", show_alert=True)


# ==================== ГРА В КОСТІ ====================

@router.callback_query(F.data == "tavern_dice_game")
async def dice_game(callback: types.CallbackQuery):
    """Азартна гра в кості"""
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    bet_amount = 20
    
    game_text = (
        f"🎲 **Гра в кості**\n\n"
        f"Правила прості: ви та Торгрім кидаєте кубик.\n"
        f"У кого більше - той виграє!\n\n"
        f"💰 Ставка: {bet_amount} золота\n"
        f"🎁 Виграш: {bet_amount * 2} золота\n\n"
        f"💰 У вас: {player.gold} золота\n\n"
        f"Хочете спробувати?"
    )
    
    if player.gold < bet_amount:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="❌ Недостатньо золота",
                callback_data="tavern_no_money"
            )],
            [types.InlineKeyboardButton(
                text="🍺 До таверни",
                callback_data="tavern_back"
            )]
        ])
    else:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="🎲 Грати!",
                callback_data="tavern_play_dice"
            )],
            [types.InlineKeyboardButton(
                text="🍺 До таверни",
                callback_data="tavern_back"
            )]
        ])
    
    await callback.message.edit_text(
        game_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "tavern_play_dice")
async def play_dice_game(callback: types.CallbackQuery):
    """Грає в кості"""
    import random
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    bet_amount = 20
    
    if player.gold < bet_amount:
        await callback.answer("❌ Недостатньо золота!", show_alert=True)
        return
    
    # Кидаємо кості
    player_roll = random.randint(1, 6)
    dealer_roll = random.randint(1, 6)
    
    # Списуємо ставку
    player.gold -= bet_amount
    
    if player_roll > dealer_roll:
        # Перемога
        player.gold += bet_amount * 2
        result = "🎉 **ПЕРЕМОГА!**"
        message = f"Ви кинули {player_roll}, Торгрім кинув {dealer_roll}!\n\nВи виграли {bet_amount * 2} золота!"
    elif player_roll == dealer_roll:
        # Нічия - повертаємо ставку
        player.gold += bet_amount
        result = "🤝 **НІЧИЯ!**"
        message = f"Обидва кинули {player_roll}!\n\nВаша ставка повернута."
    else:
        # Поразка
        result = "😢 **ПРОГРАШ...**"
        message = f"Ви кинули {player_roll}, Торгрім кинув {dealer_roll}...\n\nВи втратили {bet_amount} золота."
    
    # Зберігаємо
    await db.save_player(player.to_dict())
    
    result_text = (
        f"🎲 **Результат гри**\n\n"
        f"{result}\n\n"
        f"{message}\n\n"
        f"💰 Тепер у вас: {player.gold} золота"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="🎲 Грати ще раз",
            callback_data="tavern_dice_game"
        )],
        [types.InlineKeyboardButton(
            text="🍺 До таверни",
            callback_data="tavern_back"
        )]
    ])
    
    await callback.message.edit_text(
        result_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ==================== НАВІГАЦІЯ ====================

@router.callback_query(F.data == "tavern_back")
async def back_to_tavern(callback: types.CallbackQuery):
    """Повертається до головного меню таверни"""
    user_id = callback.from_user.id
    logger.info(f"Спроба повернутися до таверни, user_id={user_id}")
    
    db = Database()
    player_data = await db.get_player(user_id)
    
    logger.info(f"Дані гравця: {player_data is not None}")
    
    if not player_data:
        logger.error(f"Не знайдено гравця з user_id={user_id}")
        await callback.answer("❌ Помилка завантаження даних. Спробуйте /start", show_alert=True)
        return
    
    player = Player.from_dict(player_data)
    logger.info(f"Гравець завантажений: {player.character_name}")
    
    tavern_text = (
        f"🍺 **Таверна 'Гордість Вентерри'**\n\n"
        f"👤 {player.character_name}\n"
        f"💰 Золото: {player.gold}\n"
        f"❤️ HP: {player.health}/{player.max_health}\n\n"
        f"🍺 Що бажаєте?"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="🧪 Купити зілля",
            callback_data="tavern_potions"
        )],
        [types.InlineKeyboardButton(
            text="💬 Поговорити з бардом",
            callback_data="tavern_bard"
        )],
        [types.InlineKeyboardButton(
            text="🎲 Зіграти в кості",
            callback_data="tavern_dice_game"
        )],
        [types.InlineKeyboardButton(
            text="🚪 Вийти",
            callback_data="tavern_exit"
        )]
    ])
    
    try:
        await callback.message.edit_text(
            tavern_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()
        logger.info("Успішно повернулися до таверни")
    except Exception as e:
        logger.error(f"Помилка при редагуванні повідомлення: {e}")
        await callback.answer("❌ Помилка", show_alert=True)


@router.callback_query(F.data == "tavern_exit")
async def exit_tavern(callback: types.CallbackQuery):
    """Виходить з таверни"""
    await callback.message.delete()
    await callback.answer("🍺 До зустрічі у таверні!")


@router.callback_query(F.data == "tavern_no_money")
async def no_money(callback: types.CallbackQuery):
    """Повідомлення про нестачу грошей"""
    await callback.answer(
        "❌ Недостатньо золота! Ідіть на пригоди!",
        show_alert=True
    )