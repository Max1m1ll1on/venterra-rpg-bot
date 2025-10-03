# src/config/settings.py - Налаштування проекту

import os
from pathlib import Path
from dotenv import load_dotenv

# Завантажуємо .env файл
load_dotenv()

# Базові шляхи
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
MIGRATIONS_DIR = BASE_DIR / "migrations"

# Створюємо директорії якщо їх немає
try:
    LOGS_DIR.mkdir(exist_ok=True, parents=True)
except FileExistsError:
    pass  # Папка вже існує - все ок
except Exception as e:
    print(f"Попередження: не вдалося створити папку logs: {e}")

class Settings:
    """Клас налаштувань проекту"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # База даних
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(BASE_DIR / "game.db"))
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"
    
    # Логування
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = str(LOGS_DIR / "bot.log")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Режим розробки
    DEBUG: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # Налаштування гри - базові значення
    STARTING_GOLD: int = int(os.getenv("STARTING_GOLD", "1000"))  # Для тестування
    STARTING_LEVEL: int = 1
    STARTING_FREE_POINTS: int = 0  # На 1 рівні немає вільних очок
    
    # Економіка
    HEAL_COST: int = int(os.getenv("HEAL_COST", "10"))
    TEMPLE_UPGRADE_BASE_COST: int = 100
    
    # Прогресія
    EXP_MULTIPLIER: int = int(os.getenv("EXP_MULTIPLIER", "200"))
    LEVEL_STAT_BONUS: int = 1  # Скільки статів отримує гравець при рівні
    
    # Інвентар
    MAX_INVENTORY_SIZE: int = int(os.getenv("MAX_INVENTORY_SIZE", "100"))
    
    # Rate limiting (запитів на хвилину)
    RATE_LIMIT: int = 30
    
    @classmethod
    def validate(cls) -> bool:
        """Перевіряє чи всі обов'язкові налаштування встановлені"""
        if not cls.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN не встановлено! "
                "Створіть файл .env та додайте BOT_TOKEN=ваш_токен"
            )
        return True


# Створюємо екземпляр налаштувань
settings = Settings()

# Перевіряємо валідність при імпорті
if not settings.DEBUG:
    settings.validate()