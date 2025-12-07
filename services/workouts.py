"""
Сервис для работы с тренировками
"""
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Workout, UserWorkout, User
from datetime import datetime, date, timedelta
import json


async def get_workout_for_user(
    session: AsyncSession, 
    user: User, 
    day_index: int
) -> Workout | None:
    """
    Получить тренировку для пользователя на конкретный день
    day_index: 0-6 (понедельник-воскресенье)
    """
    result = await session.execute(
        select(Workout).where(
            and_(
                Workout.level == user.level,
                Workout.workout_type == user.workout_type,
                Workout.goal == user.goal,
                Workout.day_index == day_index
            )
        )
    )
    return result.scalar_one_or_none()


async def mark_workout_completed(
    session: AsyncSession,
    user_id: int,
    workout_id: int,
    feeling: str | None = None,
    comment: str | None = None
) -> UserWorkout:
    """Отметить тренировку как выполненную"""
    user_workout = UserWorkout(
        user_id=user_id,
        workout_id=workout_id,
        date=date.today(),
        completed=True,
        feeling=feeling,
        comment=comment
    )
    session.add(user_workout)
    await session.commit()
    await session.refresh(user_workout)
    return user_workout


async def get_user_workout_stats(session: AsyncSession, user_id: int, days: int = 30) -> dict:
    """
    Получить статистику тренировок пользователя
    days: количество дней для анализа
    """
    start_date = date.today() - timedelta(days=days)
    
    # Получаем все выполненные тренировки за период
    result = await session.execute(
        select(UserWorkout).where(
            and_(
                UserWorkout.user_id == user_id,
                UserWorkout.date >= start_date,
                UserWorkout.completed == True
            )
        )
    )
    workouts = list(result.scalars().all())
    
    # Подсчет статистики
    total_count = len(workouts)
    
    # Последние 7 дней
    last_7_days = date.today() - timedelta(days=7)
    count_7_days = len([w for w in workouts if w.date >= last_7_days])
    
    # Средняя оценка
    feelings = [w.feeling for w in workouts if w.feeling]
    avg_feeling = None
    if feelings:
        feeling_map = {"easy": 1, "normal": 2, "hard": 3}
        avg_value = sum(feeling_map.get(f, 2) for f in feelings) / len(feelings)
        if avg_value < 1.5:
            avg_feeling = "easy"
        elif avg_value < 2.5:
            avg_feeling = "normal"
        else:
            avg_feeling = "hard"
    
    return {
        "total": total_count,
        "last_7_days": count_7_days,
        "last_30_days": total_count,
        "average_feeling": avg_feeling
    }


async def create_workout_template(
    session: AsyncSession,
    code: str,
    title: str,
    level: str,
    workout_type: str,
    goal: str,
    day_index: int,
    exercises: list[dict]
) -> Workout:
    """Создать шаблон тренировки"""
    workout = Workout(
        code=code,
        title=title,
        level=level,
        workout_type=workout_type,
        goal=goal,
        day_index=day_index,
        exercises_json=exercises
    )
    session.add(workout)
    await session.commit()
    await session.refresh(workout)
    return workout


async def get_all_workouts(session: AsyncSession) -> list[Workout]:
    """Получить все шаблоны тренировок"""
    result = await session.execute(select(Workout))
    return list(result.scalars().all())
