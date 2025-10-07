# src/handlers/start.py - Обробник команди /start та створення персонажа

import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.database import Database
from src.models.player import Player
from src.ui.keyboards import get_class_selection_keyboard, get_city_keyboard
from src.config.constants import CLASS_NAMES, CLASS_DESCRIPTIONS
from src.handlers.states import CharacterCreation

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обробник команди /start"""
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if player_data:
        # Гравець вже існує - вітаємо повернення
        player = Player.from_dict(player_data)
        
        # ✨ Застосовуємо офлайн регенерацію
        regen_result = player.apply_regeneration()
        
        # Зберігаємо оновлений стан
        if regen_result["hp"] > 0 or regen_result["mana"] > 0:
            await db.save_player(player.to_dict())
        
        # Формуємо вітальне повідомлення
        welcome_text = f"🌍 З поверненням до Вентерри, {player.character_name}!\n\n"
        
        # Показуємо регенерацію якщо була
        if regen_result["hp"] > 0 or regen_result["mana"] > 0:
            offline_minutes = regen_result.get("offline_time", 0) // 60
            if offline_minutes > 0:
                welcome_text += f"💤 Під час вашої відсутності ({offline_minutes} хв):\n"
                if regen_result["hp"] > 0:
                    welcome_text += f"💚 Відновлено {regen_result['hp']} HP\n"
                if regen_result["mana"] > 0:
                    welcome_text += f"💙 Відновлено {regen_result['mana']} мани\n"
                welcome_text += "\n"
        
        welcome_text += (
            f"⚔️ Рівень: {player.level}\n"
            f"💰 Золото: {player.gold}\n"
            f"❤️ Здоров'я: {player.health}/{player.max_health}\n"
            f"💙 Мана: {player.mana}/{player.max_mana}\n\n"
            f"🏰 Ви знаходитесь у місті StaryFall."
        )
        
        await message.answer(
            welcome_text,
            reply_markup=get_city_keyboard()
        )
        logger.info(f"Гравець {message.from_user.id} ({player.character_name}) повернувся до гри")
    else:
        # Новий гравець - показуємо вітання
        await message.answer(
            "🌍 **Ласкаво просимо до Світу Вентерри!**\n\n"
            "Це магічний світ, сповнений пригод, небезпек та скарбів.\n"
            "Ви - відважний мандрівник, який щойно прибув до міста **StaryFall**.\n\n"
            "✨ Оберіть свій клас, щоб розпочати епічну пригоду:",
            reply_markup=get_class_selection_keyboard(),
            parse_mode="Markdown"
        )
        logger.info(f"Новий гравець {message.from_user.id} розпочав створення персонажа")
        await message.answer(
            "🌍 **Ласкаво просимо до Світу Вентерри!**\n\n"
            "Це магічний світ, сповнений пригод, небезпек та скарбів.\n"
            "Ви - відважний мандрівник, який щойно прибув до міста **StaryFall**.\n\n"
            "✨ Оберіть свій клас, щоб розпочати епічну пригоду:",
            reply_markup=get_class_selection_keyboard(),
            parse_mode="Markdown"
        )
        logger.info(f"Новий гравець {message.from_user.id} розпочав створення персонажа")


@router.callback_query(F.data.startswith("create_"))
async def select_class(callback: types.CallbackQuery, state: FSMContext):
    """Обробник вибору класу - запитує ім'я"""
    # Зберігаємо вибраний клас
    character_class = callback.data.replace("create_", "")
    await state.update_data(character_class=character_class)
    
    class_name = CLASS_NAMES[character_class]
    
    # Видаляємо старе повідомлення
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(
        f"✨ Ви обрали клас: {class_name}\n\n"
        f"👤 **Як звати вашого героя?**\n\n"
        f"Введіть ім'я персонажа (від 2 до 20 символів):",
        parse_mode="Markdown"
    )
    
    # Встановлюємо стан очікування імені
    await state.set_state(CharacterCreation.entering_name)
    await callback.answer()


@router.message(CharacterCreation.entering_name)
async def enter_character_name(message: types.Message, state: FSMContext):
    """Обробник введення імені персонажа"""
    character_name = message.text.strip()
    
    # Валідація імені
    if len(character_name) < 2:
        await message.answer(
            "❌ Ім'я занадто коротке! Мінімум 2 символи.\n"
            "Спробуйте ще раз:"
        )
        return
    
    if len(character_name) > 20:
        await message.answer(
            "❌ Ім'я занадто довге! Максимум 20 символів.\n"
            "Спробуйте ще раз:"
        )
        return
    
    # Забороняємо спецсимволи (опціонально)
    if not all(c.isalnum() or c.isspace() or c in "'-_" for c in character_name):
        await message.answer(
            "❌ Ім'я містить недозволені символи!\n"
            "Використовуйте тільки букви, цифри, пробіли, дефіс та апостроф.\n"
            "Спробуйте ще раз:"
        )
        return
    
    # Отримуємо збережений клас
    data = await state.get_data()
    character_class = data.get("character_class", "warrior")
    
    # Створюємо персонажа
    player = Player(
        user_id=message.from_user.id,
        username=message.from_user.username or message.from_user.first_name or "Гравець",
        character_name=character_name,
        character_class=character_class
    )
    
    # Зберігаємо в базу
    db = Database()
    success = await db.save_player(player.to_dict())
    
    if not success:
        await message.answer(
            "❌ Виникла помилка при створенні персонажа. Спробуйте ще раз."
        )
        await state.clear()
        return
    
    # Формуємо вітальне повідомлення
    class_name = CLASS_NAMES[character_class]
    class_description = CLASS_DESCRIPTIONS[character_class]
    
    welcome_message = (
        f"🎉 **Вітаємо, {character_name}!**\n\n"
        f"Персонаж успішно створено!\n\n"
        f"👤 **Ім'я:** {player.character_name}\n"
        f"🏅 **Клас:** {class_name}\n\n"
        f"📖 {class_description}\n\n"
        f"📊 **Початкові характеристики:**\n"
        f"💪 Сила: {player.strength}\n"
        f"🏃 Спритність: {player.agility}\n"
        f"🧠 Інтелект: {player.intelligence}\n"
        f"🛡️ Витривалість: {player.stamina}\n"
        f"🎭 Харизма: {player.charisma}\n\n"
        f"💰 Стартове золото: {player.gold}\n"
        f"❤️ Здоров'я: {player.health}/{player.max_health}\n\n"
        f"💡 **Підказка:** Вільні очки характеристик ви отримаєте "
        f"при підвищенні рівня!\n\n"
        f"🏰 Ви знаходитесь у місті **StaryFall**.\n"
        f"Використовуйте кнопки нижче для дослідження світу!"
    )
    
    await message.answer(
        welcome_message,
        reply_markup=get_city_keyboard(),
        parse_mode="Markdown"
    )
    
    # Очищуємо стан
    await state.clear()
    
    logger.info(
        f"Створено персонажа: user_id={player.user_id}, "
        f"name={player.character_name}, class={character_class}"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обробник команди /help"""
    help_text = (
        "📖 **Довідка по грі**\n\n"
        "**Команди:**\n"
        "• /start - Почати гру або повернутися\n"
        "• /help - Показати цю довідку\n\n"
        "**Як грати:**\n"
        "1️⃣ Створіть персонажа та оберіть клас\n"
        "2️⃣ Досліджуйте локації у розділі 🌲 Пригоди\n"
        "3️⃣ Бийтеся з монстрами та здобувайте досвід\n"
        "4️⃣ Покращуйте спорядження у 🏪 Магазині\n"
        "5️⃣ Розвивайте характеристики у ⛪ Храмі\n"
        "6️⃣ Виконуйте квести у 🏰 Гільдії\n\n"
        "**Локації міста:**\n"
        "🏪 Магазин - купівля та продаж предметів\n"
        "🏰 Гільдія - отримання квестів\n"
        "🍺 Таверна - покупка зілль\n"
        "⚕️ Лікар - відновлення здоров'я\n"
        "⛪ Храм - покращення характеристик\n"
        "👤 Персонаж - ваша статистика\n"
        "🎒 Інвентар - управління предметами\n"
        "🌲 Пригоди - дослідження світу\n\n"
        "💡 **Порада:** Спочатку прокачайтесь у лісі, потім досліджуйте складніші локації!"
    )
    
    await message.answer(help_text, parse_mode="Markdown")