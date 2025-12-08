"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


class Config:
    """Класс конфигурации"""
    
    # Telegram Bot
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///fitness_bot.db")
    
    # Webhook (для production)
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
    
    # Ollama AI (deprecated)
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
    
    # Groq AI (fast & free) - set via environment variable
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Fitness Center Info
    CENTER_NAME = "Fitnesss"
    CENTER_ADDRESS = "Алматы қ., Абай к-сі, 190/1"
    CENTER_LATITUDE = 43.235
    CENTER_LONGITUDE = 76.873
    CENTER_PHONE = "+77780099123"
    
    # Валидация возраста, роста, веса
    MIN_AGE = 10
    MAX_AGE = 90
    MIN_HEIGHT = 120  # см
    MAX_HEIGHT = 250  # см
    MIN_WEIGHT = 30   # кг
    MAX_WEIGHT = 300  # кг
    
    @classmethod
    def validate(cls):
        """Проверка обязательных настроек"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        return True


# Инициализация при импорте
config = Config()
