# src/models/player.py - Модель гравця (ПОВНА ВИПРАВЛЕНА ВЕРСІЯ)

import json
from typing import Dict, List, Optional

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
        self.last_login = None  # Час останнього входу
        
        # Прогресія
        self.level = 1
        self.experience = 0
        self.free_points = settings.STARTING_FREE_POINTS
        
        # Ресурси
        self.gold = settings.STARTING_GOLD
        
        # Характеристики (будуть встановлені нижче)
        self.strength = 0
        self.agility = 0
        self.intelligence = 0
        self.stamina = 0
        self.charisma = 0
        
        # Встановлюємо базові стати за класом
        self._set_base_stats()
        
        # Здоров'я
        self.max_health = self._calculate_max_health()
        self.health = self.max_health
        
        # Мана
        self.max_mana = self._calculate_max_mana()
        self.mana = self.max_mana
        
        # Навички класу
        self.class_abilities = self._get_class_abilities()
        self.ability_cooldowns = {}
        
        # Екіпірування
        self.equipment = {
            'weapon': None,
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'hands': None,
            'offhand': None,
            'ring_1': None,
            'ring_2': None,
            'earring_1': None,
            'earring_2': None,
            'amulet': None
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
        """Розраховує максимальну ману на основі інтелекту"""
        return self.intelligence * 5
    
    def _get_class_abilities(self) -> dict:
        """Повертає навички класу"""
        abilities = {
            "warrior": {
                "mighty_strike": {
                    "name": "💪 Могутній удар",
                    "description": "Наносить подвійний урон",
                    "cooldown": "1 бій",
                    "cost_type": "cooldown"
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
                    "cooldown": "1 бій",
                    "cost_type": "cooldown"
                }
            },
            "rogue": {
                "critical_strike": {
                    "name": "🗡️ Критичний удар",
                    "description": "Гарантований критичний удар (× 2.5 урону)",
                    "cooldown": "1 бій",
                    "cost_type": "cooldown"
                }
            }
        }
        return abilities.get(self.character_class, {})
    
    # ==================== ДОСВІД ТА РІВНІ ====================
    
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
        
        old_max = self.max_health
        self.max_health = self._calculate_max_health()
        health_increase = self.max_health - old_max
        self.health += health_increase
    
    # ==================== ХАРАКТЕРИСТИКИ ====================
    
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
        elif stat_name == "stamina":
            self.stamina += 1
            old_max = self.max_health
            self.max_health = self._calculate_max_health()
            self.health += (self.max_health - old_max)
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
    
    # ==================== МАНА ====================
    
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
    
    def regenerate_mana(self, in_combat: bool = False) -> int:
        """Пасивна регенерація мани на основі інтелекту"""
        if self.mana >= self.max_mana:
            return 0
        
        if in_combat:
            regen_amount = max(1, int(self.intelligence * 0.2))
        else:
            regen_amount = self.intelligence + 1
        
        return self.restore_mana(regen_amount)
    
    # ==================== НАВИЧКИ ====================
    
    def can_use_ability(self, ability_key: str) -> bool:
        """Перевіряє чи можна використати здібність"""
        if ability_key not in self.class_abilities:
            return False
        
        ability = self.class_abilities[ability_key]
        
        if ability.get("cost_type") == "cooldown":
            return ability_key not in self.ability_cooldowns
        
        if ability.get("cost_type") == "mana":
            mana_cost = ability.get("mana_cost", 0)
            return self.mana >= mana_cost
        
        return True
    
    def use_ability(self, ability_key: str) -> bool:
        """Використовує здібність"""
        if not self.can_use_ability(ability_key):
            return False
        
        ability = self.class_abilities[ability_key]
        
        if ability.get("cost_type") == "mana":
            mana_cost = ability.get("mana_cost", 0)
            self.use_mana(mana_cost)
        
        if ability.get("cost_type") == "cooldown":
            self.ability_cooldowns[ability_key] = True
        
        return True
    
    def reset_battle_cooldowns(self):
        """Скидає cooldown'и після бою"""
        self.ability_cooldowns.clear()
    
    # ==================== БІЙ ====================
    
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
            stat = self.strength + self.get_total_stat_bonus("strength")
        elif weapon_type == "ranged":
            stat = self.agility + self.get_total_stat_bonus("agility")
        elif weapon_type == "magic":
            stat = self.intelligence + self.get_total_stat_bonus("intelligence")
        else:
            stat = self.strength
        
        return (stat - 10) // 2
    
    def get_attack_power(self) -> int:
        """Розраховує силу атаки з урахуванням типу зброї"""
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
        
        base += weapon.get("strength_bonus", 0)
        base += weapon.get("agility_bonus", 0)
        base += weapon.get("intelligence_bonus", 0)
        
        return max(1, base)
    
    def get_defense(self) -> int:
        """Розраховує захист від усього спорядження"""
        defense = self.stamina // 2
        defense += self.get_total_stat_bonus("stamina") // 2
        return max(0, defense)
    
    def get_dodge_chance(self) -> float:
        """Розраховує шанс ухилення (у відсотках)"""
        return min(75.0, 5 + (self.agility * 0.5))
    
    def take_damage(self, amount: int) -> int:
        """Отримує урон і повертає фактичний урон"""
        actual_damage = max(1, amount - self.get_defense() // 2)
        self.health = max(0, self.health - actual_damage)
        self.total_damage_taken += actual_damage
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Лікує персонажа і повертає кількість відновленого HP"""
        old_health = self.health
        self.health = min(self.health + amount, self.max_health)
        return self.health - old_health
    
    def regenerate_health(self, in_combat: bool = False) -> int:
        """Пасивна регенерація здоров'я на основі витривалості"""
        if self.health >= self.max_health:
            return 0
        
        if in_combat:
            regen_amount = max(1, int(self.stamina * 0.25))
        else:
            regen_amount = self.stamina + 1
        
        return self.heal(regen_amount)
    
    def is_alive(self) -> bool:
        """Перевіряє чи живий персонаж"""
        return self.health > 0
    
    # ==================== ЕКОНОМІКА ====================
    
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
    
    # ==================== ІНВЕНТАР ====================
    
    def equip_item(self, inventory_index: int) -> bool:
        """Екіпірує предмет з інвентаря"""
        if inventory_index < 0 or inventory_index >= len(self.inventory):
            return False
        
        item = self.inventory[inventory_index]
        
        if not isinstance(item, dict) or not item.get("slot"):
            return False
        
        slot = item.get("slot")
        
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
        """Показує характеристики з урахуванням бонусів від спорядження"""
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
    
    # ==================== СЕРІАЛІЗАЦІЯ ====================
    
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
            "last_login": self.last_login,
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
        
        player.level = data.get("level", 1)
        player.experience = data.get("experience", 0)
        player.gold = data.get("gold", 100)
        player.free_points = data.get("free_points", 5)
        player.last_login = data.get("last_login")
        
        player.strength = data.get("strength", 0)
        player.agility = data.get("agility", 0)
        player.intelligence = data.get("intelligence", 0)
        player.stamina = data.get("stamina", 0)
        player.charisma = data.get("charisma", 0)
        
        player.max_health = data.get("max_health", 20)
        player.health = min(data.get("health", player.max_health), player.max_health)
        
        if "max_mana" in data and data.get("max_mana"):
            player.max_mana = data.get("max_mana")
            player.mana = min(data.get("mana", player.max_mana), player.max_mana)
        else:
            player.max_mana = player._calculate_max_mana()
            player.mana = player.max_mana
        
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
        
        try:
            player.inventory = json.loads(data.get("inventory", "[]"))
        except:
            player.inventory = []
        
        try:
            player.quests = json.loads(data.get("quests", "{}"))
        except:
            player.quests = {}
        
        try:
            player.achievements = json.loads(data.get("achievements", "[]"))
        except:
            player.achievements = []
        
        try:
            player.active_effects = json.loads(data.get("active_effects", "[]"))
        except:
            player.active_effects = []
        
        try:
            player.ability_cooldowns = json.loads(data.get("ability_cooldowns", "{}"))
        except:
            player.ability_cooldowns = {}
        
        player.current_location = data.get("current_location", "city")
        player.last_daily_reward = data.get("last_daily_reward")
        
        player.monsters_killed = data.get("monsters_killed", 0)
        player.quests_completed = data.get("quests_completed", 0)
        player.total_gold_earned = data.get("total_gold_earned", 100)
        player.total_damage_dealt = data.get("total_damage_dealt", 0)
        player.total_damage_taken = data.get("total_damage_taken", 0)
        
        return player

    # У файлі src/models/player.py
# Знайдіть метод regenerate_health (приблизно рядок 250-260)
# І ОДРАЗУ ПІСЛЯ НЬОГО додайте цей новий метод:

    def regenerate_health(self, in_combat: bool = False) -> int:
        """Пасивна регенерація здоров'я на основі витривалості"""
        if self.health >= self.max_health:
            return 0
        
        if in_combat:
            regen_amount = max(1, int(self.stamina * 0.25))
        else:
            regen_amount = self.stamina + 1
        
        return self.heal(regen_amount)
    
    # ✨ ДОДАЙТЕ ЦЕЙ НОВИЙ МЕТОД ОДРАЗУ ПІСЛЯ regenerate_health:
    def apply_offline_regeneration(self):
        """Застосовує регенерацію за час офлайну на основі stamina"""
        if not self.last_login:
            # Якщо це перший раз - встановлюємо час
            from datetime import datetime
            self.last_login = datetime.now().isoformat()
            return {"hp": 0, "mana": 0, "offline_time": 0}
        
        from datetime import datetime
        
        try:
            # Парсимо час останнього входу
            if isinstance(self.last_login, str):
                last_login_str = self.last_login.split('.')[0]
                last_login_time = datetime.fromisoformat(last_login_str)
            else:
                last_login_time = self.last_login
            
            # Розраховуємо час офлайну в секундах
            now = datetime.now()
            offline_seconds = int((now - last_login_time).total_seconds())
            
            # Якщо менше 10 секунд - не регенеруємо
            if offline_seconds < 10:
                self.last_login = now.isoformat()
                return {"hp": 0, "mana": 0, "offline_time": 0}
            
            # Регенерація на основі stamina та intelligence
            # Кожні 60 секунд = 1 тік регенерації
            regen_ticks = offline_seconds // 60
            
            # HP регенерація: (stamina + 1) за хвилину
            hp_per_tick = self.stamina + 1
            total_hp_regen = hp_per_tick * regen_ticks
            hp_regen = min(total_hp_regen, self.max_health - self.health)
            
            # Мана регенерація: (intelligence + 1) за хвилину
            mana_per_tick = self.intelligence + 1
            total_mana_regen = mana_per_tick * regen_ticks
            mana_regen = min(total_mana_regen, self.max_mana - self.mana)
            
            # Застосовуємо регенерацію
            if hp_regen > 0:
                self.health = min(self.health + hp_regen, self.max_health)
            
            if mana_regen > 0:
                self.mana = min(self.mana + mana_regen, self.max_mana)
            
            # Оновлюємо час входу
            self.last_login = now.isoformat()
            
            return {
                "hp": hp_regen,
                "mana": mana_regen,
                "offline_time": offline_seconds
            }
            
        except Exception as e:
            # Якщо помилка - просто оновлюємо last_login
            from datetime import datetime
            self.last_login = datetime.now().isoformat()
            return {"hp": 0, "mana": 0, "offline_time": 0}
    
    # Далі йдуть інші методи (is_alive, equip_item і т.д.)