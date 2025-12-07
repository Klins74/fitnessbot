"""
Управление сессиями базы данных
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from db.models import Base
from config import config


# Создание движка
engine = create_async_engine(
    config.DATABASE_URL,
    echo=False,  # Логирование SQL-запросов (для отладки можно включить)
)

# Фабрика сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Инициализация базы данных (создание таблиц)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Получение новой сессии базы данных"""
    async with async_session_maker() as session:
        yield session
