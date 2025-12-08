"""
Главный файл запуска Telegram бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from db.session import init_db, async_session_maker
from handlers import onboarding, menu, workouts, ai_handler, video_workouts, contacts

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def init_data():
    """Инициализация данных при запуске"""
    from services.achievements import init_achievements
    from load_workouts import generate_all_templates
    from services.workouts import create_workout_template
    from sqlalchemy import select
    from db.models import Workout
    
    async with async_session_maker() as session:
        # Проверяем есть ли тренировки
        result = await session.execute(select(Workout).limit(1))
        if not result.scalar_one_or_none():
            logger.info("Загрузка тренировок...")
            templates = generate_all_templates()
            for t in templates:
                try:
                    await create_workout_template(
                        session,
                        code=t["code"],
                        title=t["title"],
                        level=t["level"],
                        workout_type=t["workout_type"],
                        goal=t["goal"],
                        day_index=t["day_index"],
                        exercises=t["exercises"]
                    )
                except:
                    pass
            logger.info(f"Загружено {len(templates)} тренировок")
        
        # Инициализация достижений
        await init_achievements(session)


async def main():
    """Основная функция запуска бота"""
    # Валидация конфигурации
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        return
    
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("База данных готова")
    
    # Инициализация данных (тренировки, достижения)
    await init_data()
    logger.info("Данные инициализированы")
    
    # Создание бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключение роутеров
    dp.include_router(onboarding.router)
    dp.include_router(menu.router)
    dp.include_router(workouts.router)
    dp.include_router(ai_handler.router)
    dp.include_router(video_workouts.router)
    dp.include_router(contacts.router)
    
    logger.info("Бот запускается...")
    
    try:
        # Запуск polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
