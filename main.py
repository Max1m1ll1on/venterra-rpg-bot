# main.py - Головний файл запуску бота

import asyncio
import logging
import sys
from pathlib import Path

# Додаємо src до Python path
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config.settings import settings, LOGS_DIR
from src.database import Database

# Імпорт handlers
from src.handlers import start, city, inventory, battle, shop, tavern, guild

# Переконуємось що папка logs існує
import os
os.makedirs(LOGS_DIR, exist_ok=True)

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.FileHandler(settings.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Головна функція запуску бота"""
    
    logger.info("=" * 50)
    logger.info("Запуск Venterra RPG Bot")
    logger.info("=" * 50)
    
    # Перевірка токена
    try:
        settings.validate()
    except ValueError as e:
        logger.error(f"❌ {e}")
        return
    
    # Ініціалізація бази даних
    try:
        logger.info("Ініціалізація бази даних...")
        db = Database()
        await db.init_db()
        logger.info("✅ База даних успішно ініціалізована")
    except Exception as e:
        logger.error(f"❌ Помилка ініціалізації БД: {e}")
        return
    
    # Створення бота та диспетчера
    try:
        bot = Bot(token=settings.BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Реєстрація роутерів (ПОРЯДОК ВАЖЛИВИЙ!)
        dp.include_router(start.router)
        dp.include_router(city.router)       # City ПЕРШИЙ - обробляє кнопки
        dp.include_router(tavern.router)
        dp.include_router(inventory.router)
        dp.include_router(shop.router)
        dp.include_router(guild.router)
        dp.include_router(battle.router)     # Battle ОСТАННІЙ
        
        logger.info("✅ Бот успішно налаштований")
        logger.info("🚀 Запуск polling...")
        
        # Запуск бота
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"❌ Критична помилка: {e}", exc_info=True)
    finally:
        logger.info("Бот зупинено")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Бот зупинено користувачем (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Непередбачена помилка: {e}", exc_info=True)