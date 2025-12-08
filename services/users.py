"""
Сервис для работы с пользователями
"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from datetime import datetime


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    """Получить пользователя по telegram_id"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, telegram_id: int, user_data: dict) -> User:
    """Создать нового пользователя"""
    user = User(
        telegram_id=telegram_id,
        gender=user_data.get("gender"),
        age=user_data.get("age"),
        height_cm=user_data.get("height"),
        weight_kg=user_data.get("weight"),
        goal=user_data.get("goal"),
        level=user_data.get("level"),
        workout_type=user_data.get("workout_type"),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, telegram_id: int, user_data: dict) -> User | None:
    """Обновить данные пользователя"""
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        return None
    
    # Обновляем поля
    for key, value in user_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(user)
    return user


async def update_reminder_settings(
    session: AsyncSession, 
    telegram_id: int, 
    enabled: bool, 
    time: str | None = None,
    days: list | None = None
) -> User | None:
    """Обновить настройки напоминаний"""
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        return None
    
    user.reminder_enabled = enabled
    if time:
        user.reminder_time = time
    if days is not None:
        user.reminder_days = days
    
    user.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(user)
    return user


async def get_users_with_reminders(session: AsyncSession) -> list[User]:
    """Получить всех пользователей с включенными напоминаниями"""
    result = await session.execute(
        select(User).where(User.reminder_enabled == True)
    )
    return list(result.scalars().all())
