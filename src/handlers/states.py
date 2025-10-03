# src/handlers/states.py - Стани для створення персонажа

from aiogram.fsm.state import State, StatesGroup


class CharacterCreation(StatesGroup):
    """Стани для створення персонажа"""
    choosing_class = State()  # Вибір класу
    entering_name = State()   # Введення імені
