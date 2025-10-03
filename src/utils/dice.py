# src/utils/dice.py - Система кидків кубиків

import random
from typing import Tuple, List


class DiceRoller:
    """Клас для кидків кубиків як у D&D"""
    
    @staticmethod
    def roll(sides: int, count: int = 1) -> Tuple[int, List[int]]:
        """
        Кидає кубики
        
        Args:
            sides: Кількість граней кубика (4, 6, 8, 10, 12, 20)
            count: Кількість кубиків
            
        Returns:
            (загальна_сума, список_результатів)
        """
        rolls = [random.randint(1, sides) for _ in range(count)]
        return sum(rolls), rolls
    
    @staticmethod
    def d20() -> int:
        """Кидок d20 (для Attack Roll)"""
        return random.randint(1, 20)
    
    @staticmethod
    def d4(count: int = 1) -> Tuple[int, List[int]]:
        """Кидок d4 (магічна зброя)"""
        return DiceRoller.roll(4, count)
    
    @staticmethod
    def d6(count: int = 1) -> Tuple[int, List[int]]:
        """Кидок d6 (легка зброя, закляття)"""
        return DiceRoller.roll(6, count)
    
    @staticmethod
    def d8(count: int = 1) -> Tuple[int, List[int]]:
        """Кидок d8 (середня зброя)"""
        return DiceRoller.roll(8, count)
    
    @staticmethod
    def d10(count: int = 1) -> Tuple[int, List[int]]:
        """Кидок d10 (важка зброя)"""
        return DiceRoller.roll(10, count)
    
    @staticmethod
    def d12(count: int = 1) -> Tuple[int, List[int]]:
        """Кидок d12 (дуже важка зброя)"""
        return DiceRoller.roll(12, count)


class CombatCalculator:
    """Розрахунки для бойової системи D&D"""
    
    @staticmethod
    def attack_roll(attacker_bonus: int) -> Tuple[int, int, bool]:
        """
        Attack Roll - спроба пробити броню
        
        Returns:
            (d20_result, total_roll, is_critical)
        """
        d20_result = DiceRoller.d20()
        is_critical = (d20_result == 20)
        is_critical_fail = (d20_result == 1)
        
        if is_critical_fail:
            return d20_result, d20_result, False
        
        total = d20_result + attacker_bonus
        return d20_result, total, is_critical
    
    @staticmethod
    def damage_roll(weapon_data: dict, stat_bonus: int, is_critical: bool = False) -> Tuple[int, str]:
        """
        Damage Roll - розрахунок урону від зброї
        
        Args:
            weapon_data: Дані зброї (має містити damage_dice)
            stat_bonus: Бонус від характеристики
            is_critical: Чи критичний удар
            
        Returns:
            (урон, опис_кидка)
        """
        # Отримуємо кубики урону зброї
        damage_dice = weapon_data.get("damage_dice", "1d6")
        
        # Парсимо формат "2d6" -> (2, 6)
        if "d" in damage_dice:
            count, sides = damage_dice.split("d")
            count = int(count)
            sides = int(sides)
        else:
            count, sides = 1, 6
        
        # При критичному ударі подвоюємо кількість кубиків
        if is_critical:
            count *= 2
        
        # Кидаємо кубики
        total_damage, rolls = DiceRoller.roll(sides, count)
        
        # Додаємо бонус характеристики (тільки один раз, навіть при криті)
        total_damage += stat_bonus
        
        # Мінімум 1 урон
        total_damage = max(1, total_damage)
        
        # Формуємо опис
        rolls_str = "+".join(map(str, rolls))
        if is_critical:
            desc = f"💥 КРИТ! [{rolls_str}] + {stat_bonus} = {total_damage}"
        else:
            desc = f"[{rolls_str}] + {stat_bonus} = {total_damage}"
        
        return total_damage, desc
    
    @staticmethod
    def spell_damage(spell_dice: str, stat_bonus: int) -> Tuple[int, str]:
        """
        Урон від закляття
        
        Args:
            spell_dice: Формат "2d6"
            stat_bonus: Бонус інтелекту
            
        Returns:
            (урон, опис)
        """
        if "d" in spell_dice:
            count, sides = spell_dice.split("d")
            count = int(count)
            sides = int(sides)
        else:
            return stat_bonus, f"{stat_bonus}"
        
        total_damage, rolls = DiceRoller.roll(sides, count)
        total_damage += stat_bonus
        total_damage = max(1, total_damage)
        
        rolls_str = "+".join(map(str, rolls))
        desc = f"🔥 [{rolls_str}] + {stat_bonus} = {total_damage}"
        
        return total_damage, desc


class BattleText:
    """Текстові повідомлення для бою"""
    
    @staticmethod
    def attack_hit(attacker: str, defender: str, damage: int, damage_desc: str) -> str:
        """Повідомлення про влучну атаку"""
        return f"⚔️ {attacker} атакує {defender}!\n{damage_desc} урону"
    
    @staticmethod
    def attack_miss(attacker: str, defender: str, roll: int, target_ac: int) -> str:
        """Повідомлення про промах"""
        return f"❌ {attacker} промахнувся! ({roll} проти AC {target_ac})"
    
    @staticmethod
    def critical_hit(attacker: str) -> str:
        """Повідомлення про критичний удар"""
        return f"💥 КРИТИЧНИЙ УДАР {attacker}!"
    
    @staticmethod
    def spell_cast(caster: str, spell_name: str, damage: int) -> str:
        """Повідомлення про закляття"""
        return f"✨ {caster} використовує {spell_name}!\n💥 {damage} магічного урону"
    
    @staticmethod
    def ability_used(user: str, ability_name: str) -> str:
        """Повідомлення про використання здібності"""
        return f"⚡ {user} використовує {ability_name}!"
    
    @staticmethod
    def not_enough_mana(required: int, current: int) -> str:
        """Повідомлення про нестачу мани"""
        return f"❌ Недостатньо мани! Потрібно {required}, є {current}"