# src/handlers/battle.py - Бойова система з D&D механіками

import logging
import random
from aiogram import Router, F, types
from typing import Optional
import random

from src.database import Database
from src.models.player import Player
from src.models.monster import Monster
from src.utils.dice import DiceRoller, CombatCalculator, BattleText
from src.ui.keyboards import get_city_keyboard, get_adventure_main_keyboard
from src.config.constants import LOCATIONS
from src.utils.skill_checks import SkillCheck, get_random_event
from src.models.quest import Quest, QuestStatus

# Forward declaration для IDE
async def monster_turn(callback, battle_state, battle_log): ...

router = Router()
logger = logging.getLogger(__name__)

# Активні бої
active_battles = {}

def update_player_quests(player, event_type: str, event_detail: str = None):
    """
    Оновлює прогрес квестів гравця
    
    Args:
        player: Об'єкт гравця
        event_type: Тип події ("kill", "survive")
        event_detail: Деталі (тип монстра, локація)
    """
    if not player.quests:
        return []
    
    completed_quests = []
    
    for quest_id, quest_data in player.quests.items():
        # Пропускаємо неактивні квести
        if quest_data.get("status") != "active":
            continue
        
        quest = Quest.from_dict(quest_data)
        
        # Перевіряємо тип квесту
        if quest.quest_type.value != event_type:
            continue
        
        # Перевіряємо деталі (якщо є)
        if quest.target_detail and quest.target_detail != event_detail:
            continue
        
        # Оновлюємо прогрес
        was_completed = quest.update_progress(1)
        
        # Оновлюємо в даних гравця
        player.quests[quest_id] = quest.to_dict()
        
        if was_completed:
            completed_quests.append(quest)
    
    return completed_quests

class BattleState:
    """Стан бою з додатковими полями для D&D"""
    
    def __init__(self, player: Player, monster: Monster):
        self.player = player
        self.monster = monster
        self.abilities_used = set()
        self.round = 1
        self.battle_log = []
        
        # Тимчасові ефекти
        self.divine_shield_active = False
        
        # Лічильники використань здібностей за бій
        self.fireballs_used = 0  # Маг
        self.smite_undead_used = 0  # Паладин
        
        self.max_fireballs = 3
        self.max_smite_undead = 3
        
        # ✨ НОВЕ: Отрута розбійника
        self.poison_stacks = 0  # Кількість ходів з отрутою
        self.poison_damage = 0  # Урон отрути за хід


def get_battle_keyboard(player: Player, battle_state: BattleState) -> types.InlineKeyboardMarkup:
    """Клавіатура для бойових дій з навичками класу"""
    buttons = [
        [types.InlineKeyboardButton(text="⚔️ Атакувати", callback_data="battle_attack")],
        [types.InlineKeyboardButton(text="🛡️ Захищатися", callback_data="battle_defend")],
    ]
    
    # Додаємо кнопку навички класу
    if player.character_class == "mage":
        if player.can_use_ability("fireball") and battle_state.fireballs_used < battle_state.max_fireballs:
            buttons.append([
                types.InlineKeyboardButton(
                    text=f"🔥 Вогняний шар (5 мани) [{battle_state.fireballs_used}/{battle_state.max_fireballs}]",
                    callback_data="battle_ability_fireball"
                )
            ])
    
    elif player.character_class == "warrior":
        if "mighty_strike" not in battle_state.abilities_used:
            if player.can_use_ability("mighty_strike"):
                buttons.append([
                    types.InlineKeyboardButton(
                        text="💪 Могутній удар (6 мани, 1 раз)",
                        callback_data="battle_ability_mighty_strike"
                    )
                ])
            else:
                buttons.append([
                    types.InlineKeyboardButton(
                        text="💪 Могутній удар (❌ мало мани)",
                        callback_data="battle_no_mana"
                    )
                ])
    
    elif player.character_class == "rogue":
        if player.can_use_ability("poison_strike"):
            buttons.append([
                types.InlineKeyboardButton(
                    text="🗡️☠️ Ядовитий удар (4 мани)",
                    callback_data="battle_ability_poison_strike"
                )
            ])
    
    elif player.character_class == "paladin":
        if player.can_use_ability("divine_shield") and not battle_state.divine_shield_active:
            buttons.append([
                types.InlineKeyboardButton(
                    text="✨ Божественний щит (5 мани)",
                    callback_data="battle_ability_divine_shield"
                )
            ])
        
        if player.can_use_ability("smite_undead") and battle_state.smite_undead_used < battle_state.max_smite_undead:
            buttons.append([
                types.InlineKeyboardButton(
                    text=f"⚡ Знищення нежиті (5 мани) [{battle_state.smite_undead_used}/{battle_state.max_smite_undead}]",
                    callback_data="battle_ability_smite_undead"
                )
            ])
    
    # Кнопки зілль і втечі
    if player.inventory:
        buttons.append([
            types.InlineKeyboardButton(text="🧪 Зілля", callback_data="battle_use_potion")
        ])
    
    buttons.append([
        types.InlineKeyboardButton(text="💨 Втекти", callback_data="battle_flee")
    ])
    
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


# Додайте обробник для "немає мани"
@router.callback_query(F.data == "battle_no_mana")
async def battle_no_mana(callback: types.CallbackQuery):
    await callback.answer("❌ Недостатньо мани! Випийте зілля мани.", show_alert=True)


# ==================== ПОЧАТОК БОЮ ====================

@router.message(F.text == "🌲 Пригоди")
async def show_adventures(message: types.Message):
    """Показує меню пригод з 4 кнопками"""
    db = Database()
    player_data = await db.get_player(message.from_user.id)
    
    if not player_data:
        await message.answer("❌ Персонаж не знайдено. Використайте /start")
        return
    
    player = Player.from_dict(player_data)
    
    if player.health <= 0:
        await message.answer(
            "💀 Ви занадто ослаблені для пригод!\n"
            "Відвідайте лікаря.",
            reply_markup=get_city_keyboard()
        )
        return
    
    adventures_text = (
        f"🌲 **Пригоди у світі Вентерри**\n\n"
        f"👤 {player.character_name} (Рів. {player.level})\n"
        f"❤️ HP: {player.health}/{player.max_health}\n"
        f"💙 Мана: {player.mana}/{player.max_mana}\n"
        f"⚔️ Бонус атаки: +{player.get_attack_bonus()}\n"
        f"🛡️ AC: {player.get_armor_class()}\n\n"
        f"Ви готові до пригод! Використовуйте кнопки нижче."
    )
    
    await message.answer(
        adventures_text, 
        reply_markup=get_adventure_main_keyboard(), 
        parse_mode="Markdown"
    )


@router.message(F.text == "🗺️ Досліджувати")
async def show_exploration_menu(message: types.Message, user_id: int | None = None):
    """Показує меню досліджень з локаціями"""
    db = Database()
    uid = user_id if user_id else message.from_user.id
    player_data = await db.get_player(uid)
    
    if not player_data:
        await message.answer("❌ Персонаж не знайдено.")
        return
    
    player = Player.from_dict(player_data)
    
    # Створюємо inline клавіатуру з локаціями
    keyboard_buttons = []
    for location_id, location in LOCATIONS.items():
        if player.level >= location.get("level_required", 1):
            keyboard_buttons.append([
                types.InlineKeyboardButton(
                    text=f"{location['emoji']} {location['name']} (Рів. {location['level_required']}+)",
                    callback_data=f"explore_{location_id}"
                )
            ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(
        "🗺️ **Оберіть локацію для дослідження:**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.message(F.text == "🏰 Повернутися до міста")
async def return_to_city_button(message: types.Message):
    """Повернення до міста через кнопку"""
    user_id = message.from_user.id
    
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


@router.callback_query(F.data == "return_to_city")
async def return_to_city(callback: types.CallbackQuery):
    """Повернення до міста через inline кнопку"""
    await callback.message.delete()
    await callback.message.answer(
        "🏰 Ви повернулися до міста StaryFall.",
        reply_markup=get_city_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("explore_"))
async def explore_location(callback: types.CallbackQuery):
    """Дослідження локації з можливістю skill check"""
    location_id = callback.data.replace("explore_", "")
    
    if location_id not in LOCATIONS:
        await callback.answer("❌ Локація не знайдена!")
        return
    
    location = LOCATIONS[location_id]
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    if player.level < location.get("level_required", 1):
        await callback.answer(f"❌ Потрібен {location['level_required']} рівень!", show_alert=True)
        return
    
    # ✨ НОВЕ: 30% шанс на випадкову подію
    if random.random() < 0.3:
        event = get_random_event(location_id)
        if event:
            await show_skill_check_event(callback, location_id, location, event)
            return
    
    # Якщо події немає - звичайний бій
    await start_monster_encounter(callback, location_id, location, player)


# ============================================================
# КРОК 3: ДОДАТИ нові функції ПІСЛЯ explore_location
# ============================================================

async def show_skill_check_event(callback: types.CallbackQuery, location_id: str, location: dict, event: dict):
    """Показує подію зі skill check"""
    
    stat_names = {
        "strength": "💪 Сила",
        "agility": "🏃 Спритність",
        "intelligence": "🧠 Інтелект",
        "stamina": "🛡️ Витривалість",
        "charisma": "🎭 Харизма"
    }
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text=f"🎲 Спробувати ({stat_names[event['stat']]})",
            callback_data=f"skill_check_{location_id}_{event['stat']}"
        )],
        [types.InlineKeyboardButton(
            text="↩️ Пропустити",
            callback_data=f"skip_event_{location_id}"
        )]
    ])
    
    event_text = (
        f"{location['emoji']} **{location['name']}**\n\n"
        f"**{event['name']}**\n\n"
        f"{event['description']}\n\n"
        f"🎯 Потрібна перевірка: {stat_names[event['stat']]}\n"
        f"📊 Складність: DC {event['dc']}\n\n"
        f"Що робитимете?"
    )
    
    # Зберігаємо подію для наступної дії
    if not hasattr(explore_location, 'active_events'):
        explore_location.active_events = {}
    explore_location.active_events[callback.from_user.id] = event
    
    await callback.message.edit_text(
        event_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


async def start_monster_encounter(callback: types.CallbackQuery, location_id: str, location: dict, player):
    """Створює зустріч з монстром"""
    available_monsters = location.get("monsters", ["wolf"])
    monster_type = random.choice(available_monsters)
    
    # ✨ ВИПРАВЛЕННЯ: Рівень монстра базується на локації, а не на гравці
    location_level = location.get("level_required", 1)
    
    # Монстр може бути ±1 рівень від рівня локації
    # Але не менше 1 і не більше ніж рівень локації + 2
    monster_level = location_level + random.randint(-1, 1)
    monster_level = max(1, min(monster_level, location_level + 2))
    
    monster = Monster(monster_type, monster_level)
    
    battle_state = BattleState(player, monster)
    active_battles[callback.from_user.id] = battle_state
    
    # ✨ НОВЕ: Оновлюємо квести типу "survive"
    update_player_quests(player, "survive", location_id)
    
    # Зберігаємо оновлений прогрес
    db = Database()
    await db.save_player(player.to_dict())
    
    encounter_text = (
        f"{location['emoji']} **{location['name']}**\n\n"
        f"Ви зустріли: **{monster.name}** (Рівень {monster.level})\n\n"
        f"👹 **Противник:**\n"
        f"❤️ HP: {monster.health}/{monster.max_health}\n"
        f"🛡️ AC: {monster.defense + 10}\n"
        f"⚔️ Атака: +{monster.attack}\n\n"
        f"👤 **Ви:**\n"
        f"❤️ HP: {player.health}/{player.max_health}\n"
        f"💙 Мана: {player.mana}/{player.max_mana}\n"
        f"🛡️ AC: {player.get_armor_class()}\n"
        f"⚔️ Атака: +{player.get_attack_bonus()}\n\n"
        f"Що будете робити?"
    )
    
    await callback.message.edit_text(
        encounter_text,
        reply_markup=get_battle_keyboard(player, battle_state),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("skill_check_"))
async def handle_skill_check(callback: types.CallbackQuery):
    """Обробка спроби skill check"""
    parts = callback.data.split("_")
    location_id = parts[2]
    stat_type = parts[3]
    
    # Отримуємо збережену подію
    event = getattr(explore_location, 'active_events', {}).get(callback.from_user.id)
    if not event:
        await callback.answer("❌ Подія не знайдена!")
        return
    
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    # Отримуємо значення стату
    stat_value = getattr(player, stat_type, 10)
    
    # Виконуємо перевірку
    d20, total, success = SkillCheck.roll_check(stat_value, event['dc'])
    check_desc = SkillCheck.get_check_description(d20, total, event['dc'], success)
    
    result_text = f"🎲 **Перевірка!**\n\n{check_desc}\n\n"
    
    # Застосовуємо результат
    if success or d20 == 20:  # Критичний успіх завжди працює
        reward = event['success_reward']
        result_text += f"✨ {reward['message']}\n\n"
        
        if 'gold' in reward:
            player.add_gold(reward['gold'])
            result_text += f"💰 +{reward['gold']} золота\n"
        
        if 'exp' in reward:
            exp_result = player.add_experience(reward['exp'])
            result_text += f"⭐ +{reward['exp']} досвіду\n"
            if exp_result['leveled_up']:
                result_text += f"🎊 **НОВИЙ РІВЕНЬ {exp_result['new_level']}!**\n"
        
        if 'heal' in reward:
            healed = player.heal(reward['heal'])
            result_text += f"❤️ +{healed} HP\n"
        
        if 'item' in reward:
            result_text += f"📦 Ви знайшли цінний предмет!\n"
    
    else:  # Провал
        penalty = event['fail_penalty']
        result_text += f"💔 {penalty['message']}\n\n"
        
        if 'damage' in penalty:
            damage = penalty['damage']
            player.health -= damage
            player.health = max(1, player.health)  # Мінімум 1 HP
            player.total_damage_taken += damage
            result_text += f"💔 -{damage} HP\n"
    
    result_text += f"\n❤️ Здоров'я: {player.health}/{player.max_health}"
    
    # Зберігаємо зміни
    await db.save_player(player.to_dict())
    
    # Очищуємо збережену подію
    if hasattr(explore_location, 'active_events') and callback.from_user.id in explore_location.active_events:
        del explore_location.active_events[callback.from_user.id]
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="🌲 Продовжити дослідження",
            callback_data="continue_adventure"
        )]
    ])
    
    await callback.message.edit_text(
        result_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("skip_event_"))
async def skip_event(callback: types.CallbackQuery):
    """Пропускає подію і йде до бою"""
    location_id = callback.data.replace("skip_event_", "")
    
    # Очищуємо збережену подію
    if hasattr(explore_location, 'active_events') and callback.from_user.id in explore_location.active_events:
        del explore_location.active_events[callback.from_user.id]
    
    # Отримуємо дані для бою
    location = LOCATIONS[location_id]
    db = Database()
    player_data = await db.get_player(callback.from_user.id)
    player = Player.from_dict(player_data)
    
    await start_monster_encounter(callback, location_id, location, player)


@router.callback_query(F.data == "battle_attack")
async def battle_attack(callback: types.CallbackQuery):
    """Атака гравця з Attack Roll та анімацією кубика"""
    user_id = callback.from_user.id
    
    if user_id not in active_battles:
        await callback.answer("❌ Бій не знайдено!")
        return
    
    battle_state = active_battles[user_id]
    player = battle_state.player
    monster = battle_state.monster
    
    # ============ АНІМАЦІЯ КУБИКА ============
    import asyncio
    
    # Отримуємо поточний текст бою
    current_text = callback.message.text or ""
    
    # Анімація: кидаємо кубик
    await callback.message.edit_text(
        f"{current_text}\n\n🎲 Кидаємо кубик...",
        parse_mode="Markdown"
    )
    await asyncio.sleep(0.4)
    
    # Анімація: кубик крутиться
    await callback.message.edit_text(
        f"{current_text}\n\n🎲 Кубик крутиться...",
        parse_mode="Markdown"
    )
    await asyncio.sleep(0.4)
    
    # Розраховуємо результат
    attack_bonus = player.get_attack_bonus()
    d20_result, total_roll, is_critical = CombatCalculator.attack_roll(attack_bonus)
    
    # Анімація: показуємо результат
    await callback.message.edit_text(
        f"{current_text}\n\n🎲 Випало: **{d20_result}**!",
        parse_mode="Markdown"
    )
    await asyncio.sleep(0.5)
    # =========================================
    
    monster_ac = monster.defense + 10
    battle_log = []
    
    # Критичний промах
    if d20_result == 1:
        battle_log.append(f"💀 Критичний промах! (випало 1)")
        battle_log.append(f"Ви не наносите урону")
    
    # Попадання
    elif total_roll >= monster_ac or is_critical:
        weapon = player.equipment.get("weapon")
        
        if not weapon:
            damage = 1 + (player.strength - 10) // 2
            battle_log.append(f"🥊 Удар кулаком: {damage} урону")
        else:
            weapon_type = weapon.get("weapon_type", "melee")
            
            if weapon_type == "melee":
                stat_bonus = (player.strength + player.get_total_stat_bonus("strength") - 10) // 2
            elif weapon_type == "ranged":
                stat_bonus = (player.agility + player.get_total_stat_bonus("agility") - 10) // 2
            else:
                stat_bonus = (player.intelligence + player.get_total_stat_bonus("intelligence") - 10) // 2
            
            damage, damage_desc = CombatCalculator.damage_roll(weapon, stat_bonus, is_critical)
            
            if is_critical:
                battle_log.append(f"💥 КРИТИЧНИЙ УДАР! (випало 20)")
            
            # ✨ ПАСИВКА РОЗБІЙНИКА - Критичний удар
            if player.character_class == "rogue" and not is_critical:
                crit_chance = player.get_critical_chance()
                if random.randint(1, 100) <= crit_chance:
                    damage *= 2
                    battle_log.append(f"🗡️ ПАСИВКА: Критичний удар розбійника! ({crit_chance}%)")
                    battle_log.append(f"💥 Урон подвоєно!")
            
            battle_log.append(f"🎲 d20: {d20_result} + {attack_bonus} = {total_roll} (AC {monster_ac})")
            battle_log.append(f"⚔️ Урон: {damage_desc}")
        
        monster.health -= damage
        player.total_damage_dealt += damage
        
        # ✨ ПАСИВКА ВОЇНА - Подвійний удар
        if player.character_class == "warrior":
            double_chance = player.get_double_attack_chance()
            if random.randint(1, 100) <= double_chance:
                # Другий удар
                d20_second, total_second, is_crit_second = CombatCalculator.attack_roll(attack_bonus)
                
                battle_log.append(f"\n⚔️⚔️ ПАСИВКА: Подвійний удар! ({double_chance}%)")
                
                if total_second >= monster_ac or is_crit_second:
                    # Попадання другого удару
                    if weapon:
                        damage_second, desc_second = CombatCalculator.damage_roll(weapon, stat_bonus, is_crit_second)
                        
                        if is_crit_second:
                            battle_log.append(f"💥 Другий удар - КРИТ!")
                    else:
                        damage_second = 1 + (player.strength - 10) // 2
                        desc_second = str(damage_second)
                    
                    monster.health -= damage_second
                    player.total_damage_dealt += damage_second
                    battle_log.append(f"🎲 d20: {d20_second} → Урон: {desc_second}")
                else:
                    battle_log.append(f"❌ Другий удар промахнувся! (d20: {d20_second})")
    
    # Промах
    else:
        battle_log.append(f"❌ Промах! d20: {d20_result} + {attack_bonus} = {total_roll} (потрібно {monster_ac}+)")
    
    # Перевірка смерті монстра
    if monster.health <= 0:
        await handle_victory(callback, battle_state, battle_log)
        return
    
    # Хід монстра
    await monster_turn(callback, battle_state, battle_log)
# ↑↑↑ ТУТ ЗАКІНЧУЄТЬСЯ battle_attack ↑↑↑


# ↓↓↓ ТУТ ПОЧИНАЄТЬСЯ monster_turn ↓↓↓
async def monster_turn(callback: types.CallbackQuery, battle_state: BattleState, battle_log: list):
    """Хід монстра з анімацією"""
    import asyncio
    
    player = battle_state.player
    monster = battle_state.monster
    
    # Показуємо результат ходу гравця перед ходом монстра
    temp_text = "\n".join(battle_log)
    temp_text += f"\n\n👤 HP: {player.health}/{player.max_health}"
    temp_text += f"\n👹 {monster.name} HP: {monster.health}/{monster.max_health}"
    
    await callback.message.edit_text(
        temp_text,
        parse_mode="Markdown"
    )
    await asyncio.sleep(0.8)
    
    # ============ ХІД МОНСТРА ============
    if battle_state.divine_shield_active:
        battle_log.append(f"\n✨ Божественний щит блокує атаку!")
        battle_state.divine_shield_active = False
    else:
        # Анімація кубика монстра
        await callback.message.edit_text(
            f"{temp_text}\n\n👹 {monster.name} атакує...\n🎲 Кубик крутиться...",
            parse_mode="Markdown"
        )
        await asyncio.sleep(0.5)
        
        monster_attack_bonus = (monster.attack - 10) // 2
        d20_result, total_roll, is_critical = CombatCalculator.attack_roll(monster_attack_bonus)
        player_ac = player.get_armor_class()
        
        # Показуємо результат кубика монстра
        await callback.message.edit_text(
            f"{temp_text}\n\n👹 {monster.name} атакує...\n🎲 Випало: **{d20_result}**!",
            parse_mode="Markdown"
        )
        await asyncio.sleep(0.5)
        
        # Критичний промах
        if d20_result == 1:
            battle_log.append(f"\n💀 {monster.name} критично промахнувся!")
        
        # Попадання
        elif total_roll >= player_ac or is_critical:
            damage = max(1, monster.attack - player.get_defense() // 2)
            
            if is_critical:
                damage *= 2
                battle_log.append(f"\n💥 {monster.name} завдає КРИТИЧНИЙ УДАР!")
            
            battle_log.append(f"\n👹 {monster.name} атакує!")
            battle_log.append(f"🎲 d20: {d20_result} + {monster_attack_bonus} = {total_roll} (ваш AC {player_ac})")
            battle_log.append(f"💔 Ви отримали {damage} урону")
            
            player.health -= damage
            player.total_damage_taken += damage
        
        # Промах
        else:
            battle_log.append(f"\n👹 {monster.name} промахнувся! ({total_roll} проти AC {player_ac})")
    
    # Перевірка смерті гравця
    if player.health <= 0:
        await handle_defeat(callback, battle_state, battle_log)
        return
    
    # Наступний раунд
    battle_state.round += 1
    
    # Фінальний текст бою
    battle_text = "\n".join(battle_log)
    battle_text += f"\n\n👤 Ваше HP: {player.health}/{player.max_health}"
    battle_text += f"\n💙 Мана: {player.mana}/{player.max_mana}"
    battle_text += f"\n👹 {monster.name} HP: {monster.health}/{monster.max_health}"
    
    await callback.message.edit_text(
        battle_text,
        reply_markup=get_battle_keyboard(player, battle_state),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("battle_ability_"))
async def use_class_ability(callback: types.CallbackQuery):
    """Використання навички класу"""
    user_id = callback.from_user.id
    ability = callback.data.replace("battle_ability_", "")
    
    if user_id not in active_battles:
        await callback.answer("❌ Бій не знайдено!")
        return
    
    battle_state = active_battles[user_id]
    player = battle_state.player
    monster = battle_state.monster
    
    battle_log = []
    
    # ========== МАГ: Вогняний шар ==========
    if ability == "fireball":
        if battle_state.fireballs_used >= battle_state.max_fireballs:
            await callback.answer(f"❌ Ви вже використали Вогняний шар {battle_state.max_fireballs} рази!", show_alert=True)
            return
        
        if not player.can_use_ability("fireball"):
            await callback.answer("❌ Недостатньо мани!", show_alert=True)
            return
        
        player.use_ability("fireball")
        battle_state.fireballs_used += 1
        
        stat_bonus = (player.intelligence + player.get_total_stat_bonus("intelligence") - 10) // 2
        damage, damage_desc = CombatCalculator.spell_damage("2d6", stat_bonus)
        
        battle_log.append(f"🔥 Ви використовуєте Вогняний шар! ({battle_state.fireballs_used}/{battle_state.max_fireballs})")
        battle_log.append(f"🎲 {damage_desc}")
        
        monster.health -= damage
        player.total_damage_dealt += damage
    
    # ========== ВОЇН: Могутній удар ==========
    elif ability == "mighty_strike":
        if "mighty_strike" in battle_state.abilities_used:
            await callback.answer("❌ Ви вже використали Могутній удар!", show_alert=True)
            return
        
        if not player.can_use_ability("mighty_strike"):
            await callback.answer("❌ Недостатньо мани! (потрібно 6)", show_alert=True)
            return
        
        player.use_ability("mighty_strike")
        battle_state.abilities_used.add("mighty_strike")
        
        weapon = player.equipment.get("weapon")
        if not weapon:
            damage = int((1 + (player.strength - 10) // 2) * 2.5)
        else:
            stat_bonus = (player.strength + player.get_total_stat_bonus("strength") - 10) // 2
            base_damage, _ = CombatCalculator.damage_roll(weapon, stat_bonus, False)
            damage = int(base_damage * 2.5)
        
        battle_log.append("⚔️ Ви використовуєте Могутній удар!")
        battle_log.append(f"💥 × 2.5 урону: {damage}")
        
        monster.health -= damage
        player.total_damage_dealt += damage
    
    # ========== РОЗБІЙНИК: Ядовитий удар ==========
    elif ability == "poison_strike":
        if not player.can_use_ability("poison_strike"):
            await callback.answer("❌ Недостатньо мани! (потрібно 4)", show_alert=True)
            return
        
        player.use_ability("poison_strike")
        
        # Наносимо звичайний удар
        weapon = player.equipment.get("weapon")
        attack_bonus = player.get_attack_bonus()
        d20_result, total_roll, is_critical = CombatCalculator.attack_roll(attack_bonus)
        monster_ac = monster.defense + 10
        
        if total_roll >= monster_ac or is_critical:
            if weapon:
                stat_bonus = (player.agility + player.get_total_stat_bonus("agility") - 10) // 2
                damage, damage_desc = CombatCalculator.damage_roll(weapon, stat_bonus, is_critical)
            else:
                damage = 1 + (player.agility - 10) // 2
                damage_desc = str(damage)
            
            monster.health -= damage
            player.total_damage_dealt += damage
            
            battle_log.append(f"🗡️ Ви використовуєте Ядовитий удар!")
            battle_log.append(f"⚔️ Урон: {damage_desc}")
            
            # Накладаємо отруту на 3 ходи
            battle_state.poison_stacks = 3
            battle_state.poison_damage = random.randint(1, 4)  # 1d4
            battle_log.append(f"☠️ Отрута накладена! ({battle_state.poison_damage} урону за хід, 3 ходи)")
        else:
            battle_log.append(f"🗡️ Ядовитий удар...")
            battle_log.append(f"❌ Промах! d20: {d20_result}")
    
    # ========== ПАЛАДИН: Божественний щит ==========
    elif ability == "divine_shield":
        if battle_state.divine_shield_active:
            await callback.answer("❌ Щит вже активний!", show_alert=True)
            return
        
        if not player.can_use_ability("divine_shield"):
            await callback.answer("❌ Недостатньо мани!", show_alert=True)
            return
        
        player.use_ability("divine_shield")
        battle_state.divine_shield_active = True
        
        battle_log.append("✨ Ви активуєте Божественний щит!")
        battle_log.append("🛡️ Наступна атака монстра буде заблокована")
    
    # ========== ПАЛАДИН: Знищення нежиті ==========
    elif ability == "smite_undead":
        if battle_state.smite_undead_used >= battle_state.max_smite_undead:
            await callback.answer(f"❌ Ви вже використали Знищення нежиті {battle_state.max_smite_undead} рази!", show_alert=True)
            return
        
        if not player.can_use_ability("smite_undead"):
            await callback.answer("❌ Недостатньо мани!", show_alert=True)
            return
        
        # Перевірка чи це нежить
        undead_types = ["skeleton", "zombie", "ghost", "vampire"]
        if monster.monster_type not in undead_types:
            await callback.answer("❌ Ця здібність працює лише проти нежиті!", show_alert=True)
            return
        
        player.use_ability("smite_undead")
        battle_state.smite_undead_used += 1
        
        # Кидок 1d20 урону
        damage = random.randint(1, 20)
        
        battle_log.append(f"⚡ Ви використовуєте Знищення нежиті! ({battle_state.smite_undead_used}/{battle_state.max_smite_undead})")
        battle_log.append(f"🎲 d20: {damage} святого урону")
        
        monster.health -= damage
        player.total_damage_dealt += damage
    
    if monster.health <= 0:
        await handle_victory(callback, battle_state, battle_log)
        return
    
    await monster_turn(callback, battle_state, battle_log)


# ============================================================
# КРОК 7: Додати урон отрути в monster_turn
# ============================================================
# У функції monster_turn ПЕРЕД "Наступний раунд" додайте:

    # ✨ НОВЕ: Урон від отрути
    if battle_state.poison_stacks > 0:
        poison_dmg = battle_state.poison_damage
        monster.health -= poison_dmg
        battle_log.append(f"\n☠️ Отрута наносить {poison_dmg} урону")
        battle_state.poison_stacks -= 1
        
        if battle_state.poison_stacks > 0:
            battle_log.append(f"☠️ Отрута діє ще {battle_state.poison_stacks} ходів")
        else:
            battle_log.append(f"✓ Отрута перестала діяти")
        
        # Перевірка смерті від отрути
        if monster.health <= 0:
            await handle_victory(callback, battle_state, battle_log)
            return


async def handle_victory(callback: types.CallbackQuery, battle_state: BattleState, battle_log: list):
    """Обробка перемоги"""
    player = battle_state.player
    monster = battle_state.monster
    user_id = callback.from_user.id
    
    exp_reward = monster.exp_reward
    gold_reward = monster.gold_reward
    
    level_up_result = player.add_experience(exp_reward)
    player.add_gold(gold_reward)
    player.monsters_killed += 1
    
    player.reset_battle_cooldowns()
    
    # ✨ НОВЕ: Оновлюємо квести
    completed_quests = update_player_quests(player, "kill", monster.monster_type)
    
    db = Database()
    await db.save_player(player.to_dict())
    
    del active_battles[user_id]
    
    victory_text = "\n".join(battle_log)
    victory_text += f"\n\n🎉 **Перемога!**\n\n"
    victory_text += f"💀 {monster.name} переможено!\n"
    victory_text += f"✨ +{exp_reward} досвіду\n"
    victory_text += f"💰 +{gold_reward} золота\n"
    
    if level_up_result["leveled_up"]:
        victory_text += f"\n🎊 **НОВИЙ РІВЕНЬ {level_up_result['new_level']}!**\n"
        victory_text += f"⭐ +3 вільних очка характеристик\n"
    
    # ✨ НОВЕ: Показуємо прогрес квестів
    if completed_quests:
        victory_text += f"\n📋 **Квести:**\n"
        for quest in completed_quests:
            victory_text += f"✅ {quest.name} - ВИКОНАНО!\n"
    else:
        # Показуємо прогрес активних квестів
        active_kill_quests = [
            q for q_id, q in player.quests.items()
            if q.get("status") == "active" and q.get("type") == "kill"
        ]
        if active_kill_quests:
            victory_text += f"\n📋 **Прогрес квестів:**\n"
            for quest_data in active_kill_quests[:2]:  # Показуємо перші 2
                progress = quest_data.get("progress", 0)
                target = quest_data.get("target", 1)
                victory_text += f"🔸 {quest_data['name']}: {progress}/{target}\n"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🌲 Продовжити пригоди", callback_data="continue_adventure")]
    ])
    
    await callback.message.edit_text(victory_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()



async def handle_defeat(callback: types.CallbackQuery, battle_state: BattleState, battle_log: list):
    """Обробка поразки"""
    player = battle_state.player
    monster = battle_state.monster
    user_id = callback.from_user.id
    
    player.health = 1
    player.reset_battle_cooldowns()
    
    db = Database()
    await db.save_player(player.to_dict())
    
    del active_battles[user_id]
    
    defeat_text = "\n".join(battle_log)
    defeat_text += f"\n\n💀 **Поразка!**\n\n"
    defeat_text += f"Ви програли бій проти {monster.name}.\n"
    defeat_text += f"Поверніться до міста для відновлення."
    
    await callback.message.edit_text(defeat_text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "battle_defend")
async def battle_defend(callback: types.CallbackQuery):
    """Захист - збільшує AC на цей раунд"""
    user_id = callback.from_user.id
    
    if user_id not in active_battles:
        await callback.answer("❌ Бій не знайдено!")
        return
    
    battle_state = active_battles[user_id]
    player = battle_state.player
    
    old_stamina = player.stamina
    player.stamina += 5
    
    battle_log = ["🛡️ Ви займаєте оборонну позицію"]
    
    await monster_turn(callback, battle_state, battle_log)
    
    player.stamina = old_stamina


@router.callback_query(F.data == "battle_use_potion")
async def battle_use_potion(callback: types.CallbackQuery):
    """Показує меню зілль під час бою"""
    user_id = callback.from_user.id
    
    if user_id not in active_battles:
        await callback.answer("❌ Бій не знайдено!")
        return
    
    battle_state = active_battles[user_id]
    player = battle_state.player
    
    potions = []
    for i, item in enumerate(player.inventory):
        if isinstance(item, dict) and item.get("type") == "potion":
            potions.append((i, item))
    
    if not potions:
        await callback.answer("❌ У вас немає зілль!", show_alert=True)
        return
    
    potion_text = (
        f"🧪 **Оберіть зілля:**\n\n"
        f"❤️ HP: {player.health}/{player.max_health}\n"
        f"💙 Мана: {player.mana}/{player.max_mana}\n\n"
    )
    
    keyboard_buttons = []
    for real_index, potion in potions[:10]:
        name = potion.get("name", "Зілля")
        effect_type = potion.get("effect_type", "")
        effect_value = potion.get("effect_value", 0)
        
        # Зілля здоров'я
        if effect_type == "heal":
            keyboard_buttons.append([
                types.InlineKeyboardButton(
                    text=f"{name} (+{effect_value} HP)",
                    callback_data=f"battle_drink_{real_index}"
                )
            ])
        
        elif effect_type == "full_heal":
            keyboard_buttons.append([
                types.InlineKeyboardButton(
                    text=f"{name} (повне HP)",
                    callback_data=f"battle_drink_{real_index}"
                )
            ])
        
        # ✨ Зілля мани
        elif effect_type == "mana":
            percent = int(effect_value * 100)
            keyboard_buttons.append([
                types.InlineKeyboardButton(
                    text=f"{name} (+{percent}% мани)",
                    callback_data=f"battle_drink_{real_index}"
                )
            ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(text="🔙 Назад", callback_data="battle_back")
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(potion_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "battle_back")
async def battle_back_to_menu(callback: types.CallbackQuery):
    """Повернення до меню бою"""
    user_id = callback.from_user.id
    
    if user_id not in active_battles:
        await callback.answer("❌ Бій не знайдено!")
        return
    
    battle_state = active_battles[user_id]
    player = battle_state.player
    monster = battle_state.monster
    
    battle_text = (
        f"⚔️ **Бій**\n\n"
        f"👤 Ваше HP: {player.health}/{player.max_health}\n"
        f"💙 Мана: {player.mana}/{player.max_mana}\n"
        f"👹 {monster.name} HP: {monster.health}/{monster.max_health}\n\n"
        f"Що робити?"
    )
    
    await callback.message.edit_text(
        battle_text,
        reply_markup=get_battle_keyboard(player, battle_state),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("battle_drink_"))
async def battle_drink_potion(callback: types.CallbackQuery):
    """Використовує зілля під час бою"""
    user_id = callback.from_user.id
    real_index_str = callback.data.replace("battle_drink_", "")
    
    try:
        real_index = int(real_index_str)
    except ValueError:
        await callback.answer("❌ Помилка!")
        return
    
    if user_id not in active_battles:
        await callback.answer("❌ Бій не знайдено!")
        return
    
    battle_state = active_battles[user_id]
    player = battle_state.player
    monster = battle_state.monster
    
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
    
    current_hp = player.health
    max_hp = player.max_health
    
    battle_log = []
    
    # ========== ЗІЛЛЯ ЗДОРОВ'Я ==========
    if effect_type == "heal":
        if current_hp >= max_hp:
            await callback.answer("❤️ Ви вже на повному здоров'ї!", show_alert=True)
            return
        
        healed = min(effect_value, max_hp - current_hp)
        player.health += healed
        battle_log.append(f"🧪 Ви випили {potion_name}")
        battle_log.append(f"❤️ Відновлено {healed} HP")
        
    elif effect_type == "full_heal":
        if current_hp >= max_hp:
            await callback.answer("❤️ Ви вже на повному здоров'ї!", show_alert=True)
            return
        
        healed = max_hp - current_hp
        player.health = max_hp
        battle_log.append(f"🧪 Ви випили {potion_name}")
        battle_log.append(f"✨ Повністю відновлено! (+{healed} HP)")
    
    # ========== ✨ НОВЕ: ЗІЛЛЯ МАНИ ==========
    elif effect_type == "mana":
        current_mana = player.mana
        max_mana = player.max_mana
        
        if current_mana >= max_mana:
            await callback.answer("💙 Ви вже на повній мані!", show_alert=True)
            return
        
        # effect_value - це % (0.25, 0.5, 1.0)
        mana_restored = int(max_mana * effect_value)
        mana_restored = min(mana_restored, max_mana - current_mana)
        
        player.mana += mana_restored
        battle_log.append(f"🧪 Ви випили {potion_name}")
        battle_log.append(f"💙 Відновлено {mana_restored} мани")
    
    # ========== НЕВІДОМИЙ ТИП ==========
    else:
        await callback.answer("❌ Невідомий тип зілля!")
        return
    
    # Видаляємо зілля з інвентаря
    player.inventory.pop(real_index)
    
    # Зберігаємо зміни
    db = Database()
    await db.save_player(player.to_dict())
    
    # Хід монстра після використання зілля
    await monster_turn(callback, battle_state, battle_log)


@router.callback_query(F.data == "battle_flee")
async def battle_flee(callback: types.CallbackQuery):
    """Спроба втечі"""
    user_id = callback.from_user.id
    
    if user_id not in active_battles:
        await callback.answer("❌ Бій не знайдено!")
        return
    
    battle_state = active_battles[user_id]
    player = battle_state.player
    
    # Шанс втечі: 50% + бонус спритності
    flee_chance = 50 + (player.agility * 2)
    roll = random.randint(1, 100)
    
    if roll <= flee_chance:
        # Успішна втеча
        player.reset_battle_cooldowns()
        
        db = Database()
        await db.save_player(player.to_dict())
        
        del active_battles[user_id]
        
        await callback.message.edit_text(
            f"💨 Ви успішно втекли!\n"
            f"Шанс втечі: {flee_chance}%\n"
            f"Кидок: {roll}",
            parse_mode="Markdown"
        )
    else:
        # Невдала втеча - монстр атакує
        battle_log = [f"💨 Спроба втечі невдала! ({roll}/{flee_chance})"]
        await monster_turn(callback, battle_state, battle_log)
    
    await callback.answer()


@router.callback_query(F.data == "continue_adventure")
async def continue_adventure(callback: types.CallbackQuery):
    """Продовжує пригоди після перемоги"""
    await show_exploration_menu(callback.message, callback.from_user.id)