# src/models/player.py - Модель гравця (ОПТИМІЗОВАНА ВЕРСІЯ)

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from src.config.constants import CLASS_BASE_STATS, CharacterClass
from src.config.settings import settings


class Player:
    """Модель гравця у грі"""
    
    def __init__(self, user_id: int, username: str = "", character_name: str = "", character_class: str = "warrior"):
        # Ідентифікація
        self.user_id = user_id
        self.username = username
        self.character_name = character_name or "Безіменний"
        self.character_class = character_class
        
        # ✨ ВАЖЛИВО: Єдине поле для регенерації
        self.last_regeneration_time = datetime.now().isoformat()
        
        # Прогресія
        self.level = 1
        self.experience = 0
        self.free_points = settings.STARTING_FREE_POINTS
        
        # Ресурси
        self.gold = settings.STARTING_GOLD
        
        # Характеристики
        self.strength = 0
        self.agility = 0
        self.intelligence = 0
        self.stamina = 0
        self.charisma = 0
        
        # Встановлюємо базові стати за класом
        self._set_base_stats()
        
        # Здоров'я та мана
        self.max_health = self._calculate_max_health()
        self.health = self.max_health
        self.max_mana = self._calculate_max_mana()
        self.mana = self.max_mana
        
        # Навички класу
        self.class_abilities = self._get_class_abilities()
        self.ability_cooldowns = {}
        
        # Екіпірування (12 слотів)
        self.equipment = {
            'weapon': None, 'head': None, 'chest': None, 'legs': None,
            'feet': None, 'hands': None, 'offhand': None,
            'ring_1': None, 'ring_2': None, 'earring_1': None,
            'earring_2': None, 'amulet': None
        }
        
        # Інвентар
        self.inventory = []
        
        # Локація
        self.current_location = "city"
        
        # Квести
        self.quests = {}
        
        # Статистика
        self.monsters_killed = 0
        self.quests_completed = 0
        self.total_gold_earned = settings.STARTING_GOLD
        self.total_damage_dealt = 0
        self.total_damage_taken = 0
        
        # Досягнення
        self.achievements = []
        self.last_daily_reward = None
        
        # Активні ефекти
        self.active_effects = []
    
    # =====================================================
    # 🔥 ЄДИНА СИСТЕМА РЕГЕНЕРАЦІЇ
    # =====================================================
    
    def apply_regeneration(self, force_update: bool = True) -> Dict[str, int]:
        """
        ЄДИНА функція регенерації для всієї гри
        
        Формула:
        - Кожні 60 секунд = 1 тік регенерації
        - HP за тік = stamina + 1
        - Мана за тік = intelligence + 1
        
        Args:
            force_update: Чи оновлювати час останньої регенерації
            
        Returns:
            Словник з інформацією про регенерацію
        """
        # Парсимо час останньої регенерації
        if not self.last_regeneration_time:
            self.last_regeneration_time = datetime.now().isoformat()
            return {"hp": 0, "mana": 0, "seconds": 0, "ticks": 0}
        
        try:
            # Підтримка різних форматів часу
            if isinstance(self.last_regeneration_time, str):
                last_time = datetime.fromisoformat(self.last_regeneration_time.split('.')[0])
            else:
                last_time = self.last_regeneration_time
            
            now = datetime.now()
            elapsed_seconds = int((now - last_time).total_seconds())
            
            # Менше 60 секунд - немає регенерації
            if elapsed_seconds < 60:
                return {"hp": 0, "mana": 0, "seconds": elapsed_seconds, "ticks": 0}
            
            # =====================================================
            # ЄДИНА ФОРМУЛА РЕГЕНЕРАЦІЇ
            # =====================================================
            regen_ticks = elapsed_seconds // 60
            
            # HP регенерація
            hp_per_tick = self.stamina + 1
            max_hp_to_regen = self.max_health - self.health
            hp_regen = min(hp_per_tick * regen_ticks, max_hp_to_regen)
            
            # Мана регенерація
            mana_per_tick = self.intelligence + 1
            max_mana_to_regen = self.max_mana - self.mana
            mana_regen = min(mana_per_tick * regen_ticks, max_mana_to_regen)
            
            # Застосовуємо регенерацію
            if hp_regen > 0:
                self.health = min(self.health + hp_regen, self.max_health)
            
            if mana_regen > 0:
                self.mana = min(self.mana + mana_regen, self.max_mana)
            
            # Оновлюємо час останньої регенерації
            if force_update and (hp_regen > 0 or mana_regen > 0):
                self.last_regeneration_time = now.isoformat()
            
            return {
                "hp": hp_regen,
                "mana": mana_regen,
                "seconds": elapsed_seconds,
                "ticks": regen_ticks
            }
            
        except Exception as e:
            print(f"Помилка регенерації: {e}")
            self.last_regeneration_time = datetime.now().isoformat()
            return {"hp": 0, "mana": 0, "seconds": 0, "ticks": 0}
    
    def apply_offline_regeneration(self) -> Dict[str, int]:
        """
        Застаріла функція - для зворотної сумісності
        Використовує нову систему регенерації
        """
        result = self.apply_regeneration()
        return {
            "hp": result["hp"],
            "mana": result["mana"],
            "offline_time": result["seconds"]
        }
    
    # =====================================================
    # БАЗОВІ МЕТОДИ
    # =====================================================
    
    def _set_base_stats(self):
        """Встановлює базові характеристики за класом"""
        stats = CLASS_BASE_STATS.get(self.character_class, CLASS_BASE_STATS[CharacterClass.WARRIOR])
        self.strength = stats["strength"]
        self.agility = stats["agility"]
        self.intelligence = stats["intelligence"]
        self.stamina = stats["stamina"]
        self.charisma = stats["charisma"]
    
    def _calculate_max_health(self) -> int:
        """Розраховує максимальне здоров'я"""
        return 20 + (self.stamina * 5)
    
    def _calculate_max_mana(self) -> int:
        """Розраховує максимальну ману"""
        return self.intelligence * 5
    
    def _get_class_abilities(self) -> dict:
        """Повертає навички класу"""
        abilities = {
            "warrior": {
                "mighty_strike": {
                    "name": "💪 Могутній удар",
                    "description": "Наносить подвійний урон",
                    "mana_cost": 6,
                    "cost_type": "mana"
                }
            },
            "mage": {
                "fireball": {
                    "name": "🔥 Вогняний шар",
                    "description": "Магічна атака (2d6 + Інтелект урону)",
                    "mana_cost": 5,
                    "cost_type": "mana"
                }
            },
            "paladin": {
                "divine_shield": {
                    "name": "✨ Божественний щит",
                    "description": "Блокує наступну атаку ворога",
                    "mana_cost": 5,
                    "cost_type": "mana"
                },
                "smite_undead": {
                    "name": "⚡ Знищення нежиті",
                    "description": "1d20 урону по нежиті",
                    "mana_cost": 5,
                    "cost_type": "mana"
                }
            },
            "rogue": {
                "poison_strike": {
                    "name": "🗡️☠️ Ядовитий удар",
                    "description": "Атака з отрутою (1d4 урону 3 ходи)",
                    "mana_cost": 4,
                    "cost_type": "mana"
                }
            }
        }
        return abilities.get(self.character_class, {})
    
    # =====================================================
    # ПРОГРЕСІЯ
    # =====================================================
    
    def get_required_experience(self) -> int:
        """Повертає необхідну кількість досвіду для наступного рівня"""
        return settings.EXP_MULTIPLIER * self.level
    
    def add_experience(self, amount: int) -> Dict:
        """Додає досвід та перевіряє підвищення рівня"""
        self.experience += amount
        
        result = {
            "leveled_up": False,
            "old_level": self.level,
            "new_level": self.level,
            "exp_gained": amount,
        }
        
        required_exp = self.get_required_experience()
        if self.experience >= required_exp:
            result["leveled_up"] = True
            result["old_level"] = self.level
            self.level_up()
            result["new_level"] = self.level
        
        return result
    
    def level_up(self):
        """Підвищує рівень персонажа"""
        self.level += 1
        self.experience = 0
        self.free_points += 3
        
        # Оновлюємо максимальні значення
        old_max_health = self.max_health
        old_max_mana = self.max_mana
        
        self.max_health = self._calculate_max_health()
        self.max_mana = self._calculate_max_mana()
        
        # Додаємо різницю до поточних значень
        health_increase = self.max_health - old_max_health
        mana_increase = self.max_mana - old_max_mana
        
        self.health = min(self.health + health_increase, self.max_health)
        self.mana = min(self.mana + mana_increase, self.max_mana)
    
    # =====================================================
    # ХАРАКТЕРИСТИКИ
    # =====================================================
    
    def add_stat(self, stat_name: str) -> bool:
        """Додає 1 очко до характеристики"""
        if self.free_points <= 0:
            return False
        
        if stat_name == "strength":
            self.strength += 1
        elif stat_name == "agility":
            self.agility += 1
        elif stat_name == "intelligence":
            self.intelligence += 1
            # Оновлюємо максимальну ману
            old_max_mana = self.max_mana
            self.max_mana = self._calculate_max_mana()
            self.mana += (self.max_mana - old_max_mana)
        elif stat_name == "stamina":
            self.stamina += 1
            # Оновлюємо максимальне здоров'я
            old_max_health = self.max_health
            self.max_health = self._calculate_max_health()
            self.health += (self.max_health - old_max_health)
        elif stat_name == "charisma":
            self.charisma += 1
        else:
            return False
        
        self.free_points -= 1
        return True
    
    def get_total_stat_bonus(self, stat_name: str) -> int:
        """Отримує загальний бонус характеристики від спорядження"""
        bonus = 0
        bonus_key = f"{stat_name}_bonus"
        
        for slot, item in self.equipment.items():
            if item and isinstance(item, dict):
                bonus += item.get(bonus_key, 0)
        
        return bonus
    
    # =====================================================
    # МАНА ТА ЗДІБНОСТІ
    # =====================================================
    
    def use_mana(self, amount: int) -> bool:
        """Витрачає ману"""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False
    
    def restore_mana(self, amount: int) -> int:
        """Відновлює ману і повертає кількість відновленої мани"""
        old_mana = self.mana
        self.mana = min(self.mana + amount, self.max_mana)
        return self.mana - old_mana
    
    def can_use_ability(self, ability_name: str) -> bool:
        """Перевіряє чи може використати здібність"""
        if ability_name not in self.class_abilities:
            return False
        
        ability = self.class_abilities[ability_name]
        mana_cost = ability.get("mana_cost", 0)
        
        return self.mana >= mana_cost
    
    def use_ability(self, ability_name: str) -> bool:
        """Використовує здібність"""
        if not self.can_use_ability(ability_name):
            return False
        
        ability = self.class_abilities[ability_name]
        mana_cost = ability.get("mana_cost", 0)
        
        self.mana -= mana_cost
        return True
    
    def reset_battle_cooldowns(self):
        """Скидає кулдауни здібностей після бою"""
        self.ability_cooldowns = {}
    
    # =====================================================
    # БОЙОВІ ХАРАКТЕРИСТИКИ
    # =====================================================
    
    def get_armor_class(self) -> int:
        """Розраховує Armor Class (AC) як у D&D"""
        base_ac = 10
        dex_bonus = min(5, (self.agility + self.get_total_stat_bonus("agility")) // 2)
        armor_bonus = (self.stamina + self.get_total_stat_bonus("stamina")) // 3
        return base_ac + dex_bonus + armor_bonus
    
    def get_attack_bonus(self) -> int:
        """Розраховує бонус до атаки для Attack Roll"""
        weapon = self.equipment.get("weapon")
        
        if not weapon:
            return (self.strength - 10) // 2
        
        weapon_type = weapon.get("weapon_type", "melee")
        
        if weapon_type == "melee":
            stat = self.strength + self.get_total_stat_bonus("strength") + self.get_active_buff_bonus("strength")
        elif weapon_type == "ranged":
            stat = self.agility + self.get_total_stat_bonus("agility") + self.get_active_buff_bonus("agility")
        elif weapon_type == "magic":
            stat = self.intelligence + self.get_total_stat_bonus("intelligence") + self.get_active_buff_bonus("intelligence")
        else:
            stat = self.strength
        
        return (stat - 10) // 2
    
    def get_attack_power(self) -> int:
        """Розраховує силу атаки"""
        weapon = self.equipment.get("weapon")
        
        if not weapon:
            return max(1, self.strength)
        
        weapon_type = weapon.get("weapon_type", "melee")
        
        if weapon_type == "melee":
            base = self.strength + self.get_total_stat_bonus("strength")
        elif weapon_type == "ranged":
            base = self.agility + self.get_total_stat_bonus("agility")
        elif weapon_type == "magic":
            base = self.intelligence + self.get_total_stat_bonus("intelligence")
        else:
            base = self.strength
        
        # Додаємо бонуси від зброї
        base += weapon.get("strength_bonus", 0)
        base += weapon.get("agility_bonus", 0)
        base += weapon.get("intelligence_bonus", 0)
        
        return max(1, base)
    
    def get_defense(self) -> int:
        """Розраховує захист"""
        defense = self.stamina // 2
        defense += self.get_total_stat_bonus("stamina") // 2
        return max(0, defense)
    
    def get_dodge_chance(self) -> float:
        """Розраховує шанс ухилення"""
        return min(75.0, 5 + (self.agility * 0.5))
    
    def get_double_attack_chance(self) -> int:
        """Шанс подвійного удару воїна"""
        if self.character_class != "warrior":
            return 0
        
        base_chance = 25
        strength_bonus = max(0, (self.strength - 10) * 2)
        return min(75, base_chance + strength_bonus)
    
    def get_critical_chance(self) -> int:
        """Шанс критичного удару розбійника"""
        if self.character_class != "rogue":
            return 0
        
        base_chance = 25
        agility_bonus = max(0, (self.agility - 10) * 2)
        return min(75, base_chance + agility_bonus)
    
    # =====================================================
    # ЗДОРОВ'Я ТА УРОН
    # =====================================================
    
    def take_damage(self, amount: int) -> int:
        """Отримує урон і повертає фактичний урон"""
        actual_damage = max(1, amount - self.get_defense() // 2)
        self.health = max(0, self.health - actual_damage)
        self.total_damage_taken += actual_damage
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Лікує персонажа"""
        old_health = self.health
        self.health = min(self.health + amount, self.max_health)
        return self.health - old_health
    
    def is_alive(self) -> bool:
        """Перевіряє чи живий персонаж"""
        return self.health > 0
    
    # =====================================================
    # ЕКОНОМІКА
    # =====================================================
    
    def add_gold(self, amount: int):
        """Додає золото"""
        self.gold += amount
        self.total_gold_earned += amount
    
    def spend_gold(self, amount: int) -> bool:
        """Витрачає золото"""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    # =====================================================
    # ІНВЕНТАР ТА ЕКІПІРУВАННЯ
    # =====================================================
    
    def equip_item(self, inventory_index: int) -> bool:
        """Екіпірує предмет з інвентаря"""
        if inventory_index < 0 or inventory_index >= len(self.inventory):
            return False
        
        item = self.inventory[inventory_index]
        
        if not isinstance(item, dict) or not item.get("slot"):
            return False
        
        slot = item.get("slot")
        
        # Обробка подвійних слотів (кільця та сережки)
        if slot in ["ring_1", "ring_2"]:
            if self.equipment.get("ring_1") is None:
                target_slot = "ring_1"
            elif self.equipment.get("ring_2") is None:
                target_slot = "ring_2"
            else:
                target_slot = "ring_1"
                if self.equipment["ring_1"]:
                    self.inventory.append(self.equipment["ring_1"])
        
        elif slot in ["earring_1", "earring_2"]:
            if self.equipment.get("earring_1") is None:
                target_slot = "earring_1"
            elif self.equipment.get("earring_2") is None:
                target_slot = "earring_2"
            else:
                target_slot = "earring_1"
                if self.equipment["earring_1"]:
                    self.inventory.append(self.equipment["earring_1"])
        
        else:
            target_slot = slot
            if self.equipment.get(target_slot):
                self.inventory.append(self.equipment[target_slot])
        
        self.equipment[target_slot] = item
        self.inventory.pop(inventory_index)
        
        return True
    
    def unequip_item(self, slot: str) -> bool:
        """Знімає предмет зі слоту"""
        if slot not in self.equipment:
            return False
        
        if not self.equipment[slot]:
            return False
        
        self.inventory.append(self.equipment[slot])
        self.equipment[slot] = None
        
        return True
    
    # =====================================================
    # БАФИ ТА ЕФЕКТИ
    # =====================================================
    
    def get_active_buff_bonus(self, stat_name: str) -> int:
        """Отримує бонус від активних бафів"""
        bonus = 0
        active_buffs = []
        
        for effect in self.active_effects:
            if effect.get("type") == "buff" and effect.get("stat") == stat_name:
                try:
                    expires_at = datetime.fromisoformat(effect["expires_at"])
                    if datetime.now() < expires_at:
                        bonus += effect.get("value", 0)
                        active_buffs.append(effect)
                except:
                    pass
        
        # Оновлюємо список - залишаємо тільки активні
        self.active_effects = active_buffs
        
        return bonus
    
    def clean_expired_buffs(self):
        """Видаляє прострочені бафи"""
        active = []
        for effect in self.active_effects:
            if effect.get("type") == "buff":
                try:
                    expires_at = datetime.fromisoformat(effect["expires_at"])
                    if datetime.now() < expires_at:
                        active.append(effect)
                except:
                    pass
            else:
                active.append(effect)
        
        self.active_effects = active
    
    # =====================================================
    # ВІДОБРАЖЕННЯ
    # =====================================================
    
    def get_equipment_display(self) -> str:
        """Форматує відображення екіпірування"""
        try:
            from src.config.equipment import RARITY_EMOJI
        except ImportError:
            RARITY_EMOJI = {
                "common": "⚪",
                "uncommon": "🟢",
                "rare": "🔵",
                "epic": "🟣",
                "legendary": "🟠"
            }
        
        equipment_lines = []
        
        slot_names = {
            "weapon": "⚔️ Зброя",
            "head": "⛑️ Шолом",
            "chest": "👕 Нагрудник",
            "legs": "👖 Набедреник",
            "feet": "👢 Взуття",
            "hands": "🧤 Рукавиці",
            "offhand": "🛡️ Щит",
            "ring_1": "💍 Перстень 1",
            "ring_2": "💍 Перстень 2",
            "earring_1": "💎 Сережка 1",
            "earring_2": "💎 Сережка 2",
            "amulet": "📿 Амулет"
        }
        
        for slot, slot_name in slot_names.items():
            item = self.equipment.get(slot)
            if item:
                rarity = item.get("rarity", "common")
                rarity_emoji = RARITY_EMOJI.get(rarity, "⚪")
                item_name = item.get("name", "Предмет")
                equipment_lines.append(f"{slot_name}: {rarity_emoji} {item_name}")
            else:
                equipment_lines.append(f"{slot_name}: *порожньо*")
        
        return "\n".join(equipment_lines)
    
    def get_total_stats_display(self) -> str:
        """Показує характеристики з бонусами"""
        str_bonus = self.get_total_stat_bonus("strength")
        agi_bonus = self.get_total_stat_bonus("agility")
        int_bonus = self.get_total_stat_bonus("intelligence")
        sta_bonus = self.get_total_stat_bonus("stamina")
        cha_bonus = self.get_total_stat_bonus("charisma")
        
        lines = [
            f"💪 Сила: {self.strength}" + (f" (+{str_bonus})" if str_bonus else ""),
            f"🏃 Спритність: {self.agility}" + (f" (+{agi_bonus})" if agi_bonus else ""),
            f"🧠 Інтелект: {self.intelligence}" + (f" (+{int_bonus})" if int_bonus else ""),
            f"🛡️ Витривалість: {self.stamina}" + (f" (+{sta_bonus})" if sta_bonus else ""),
            f"✨ Харизма: {self.charisma}" + (f" (+{cha_bonus})" if cha_bonus else "")
        ]
        
        return "\n".join(lines)
    
    # =====================================================
    # СЕРІАЛІЗАЦІЯ
    # =====================================================
    
    def to_dict(self) -> Dict:
        """Конвертує у словник для збереження в БД"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "character_name": self.character_name,
            "class": self.character_class,
            "level": self.level,
            "experience": self.experience,
            "gold": self.gold,
            "strength": self.strength,
            "agility": self.agility,
            "intelligence": self.intelligence,
            "stamina": self.stamina,
            "charisma": self.charisma,
            "free_points": self.free_points,
            "health": self.health,
            "max_health": self.max_health,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "equipment": json.dumps(self.equipment, ensure_ascii=False),
            "inventory": json.dumps(self.inventory, ensure_ascii=False),
            "current_location": self.current_location,
            "quests": json.dumps(self.quests, ensure_ascii=False),
            "achievements": json.dumps(self.achievements, ensure_ascii=False),
            "last_daily_reward": self.last_daily_reward,
            "monsters_killed": self.monsters_killed,
            "quests_completed": self.quests_completed,
            "total_gold_earned": self.total_gold_earned,
            "total_damage_dealt": self.total_damage_dealt,
            "total_damage_taken": self.total_damage_taken,
            "active_effects": json.dumps(self.active_effects, ensure_ascii=False),
            "ability_cooldowns": json.dumps(self.ability_cooldowns, ensure_ascii=False),
            # Підтримка обох полів для сумісності
            "last_login": self.last_regeneration_time,
            "last_regeneration": self.last_regeneration_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Player":
        """Створює об'єкт з словника з БД"""
        player = cls(
            user_id=data["user_id"],
            username=data.get("username", ""),
            character_name=data.get("character_name", "Безіменний"),
            character_class=data.get("class", "warrior")
        )
        
        # Основні дані
        player.level = data.get("level", 1)
        player.experience = data.get("experience", 0)
        player.gold = data.get("gold", 100)
        player.free_points = data.get("free_points", 5)
        
        # ✨ Міграція полів регенерації (підтримка старих баз)
        if "last_regeneration" in data and data["last_regeneration"]:
            player.last_regeneration_time = data["last_regeneration"]
        elif "last_login" in data and data["last_login"]:
            player.last_regeneration_time = data["last_login"]
        else:
            player.last_regeneration_time = datetime.now().isoformat()
        
        # Характеристики
        player.strength = data.get("strength", 10)
        player.agility = data.get("agility", 10)
        player.intelligence = data.get("intelligence", 10)
        player.stamina = data.get("stamina", 10)
        player.charisma = data.get("charisma", 10)
        
        # Здоров'я та мана
        player.max_health = data.get("max_health", 100)
        player.health = min(data.get("health", player.max_health), player.max_health)
        
        if "max_mana" in data and data.get("max_mana"):
            player.max_mana = data.get("max_mana")
            player.mana = min(data.get("mana", player.max_mana), player.max_mana)
        else:
            player.max_mana = player._calculate_max_mana()
            player.mana = player.max_mana
        
        # Екіпірування
        try:
            equipment_data = json.loads(data.get("equipment", "{}"))
            default_equipment = {
                'weapon': None, 'head': None, 'chest': None, 'legs': None,
                'feet': None, 'hands': None, 'offhand': None,
                'ring_1': None, 'ring_2': None, 'earring_1': None,
                'earring_2': None, 'amulet': None
            }
            default_equipment.update(equipment_data)
            player.equipment = default_equipment
        except:
            player.equipment = {
                'weapon': None, 'head': None, 'chest': None, 'legs': None,
                'feet': None, 'hands': None, 'offhand': None,
                'ring_1': None, 'ring_2': None, 'earring_1': None,
                'earring_2': None, 'amulet': None
            }
        
        # Інвентар
        try:
            player.inventory = json.loads(data.get("inventory", "[]"))
        except:
            player.inventory = []
        
        # Квести
        try:
            player.quests = json.loads(data.get("quests", "{}"))
        except:
            player.quests = {}
        
        # Досягнення
        try:
            player.achievements = json.loads(data.get("achievements", "[]"))
        except:
            player.achievements = []
        
        # Активні ефекти
        try:
            player.active_effects = json.loads(data.get("active_effects", "[]"))
        except:
            player.active_effects = []
        
        # Кулдауни здібностей
        try:
            player.ability_cooldowns = json.loads(data.get("ability_cooldowns", "{}"))
        except:
            player.ability_cooldowns = {}
        
        # Інші дані
        player.current_location = data.get("current_location", "city")
        player.last_daily_reward = data.get("last_daily_reward")
        
        # Статистика
        player.monsters_killed = data.get("monsters_killed", 0)
        player.quests_completed = data.get("quests_completed", 0)
        player.total_gold_earned = data.get("total_gold_earned", 100)
        player.total_damage_dealt = data.get("total_damage_dealt", 0)
        player.total_damage_taken = data.get("total_damage_taken", 0)
        
        return player