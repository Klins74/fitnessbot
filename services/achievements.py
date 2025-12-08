"""
Сервис для работы с достижениями и streak
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, UserWorkout, Achievement, UserAchievement
from datetime import date, timedelta


# Определение достижений
ACHIEVEMENTS = [
    {"code": "first_workout", "title": "Бірінші жаттығу", "emoji": "🎯", "description": "Алғашқы жаттығуды аяқтадың!"},
    {"code": "streak_3", "title": "3 күн серия", "emoji": "🔥", "description": "3 күн қатарынан жаттықтың!"},
    {"code": "streak_7", "title": "7 күн серия", "emoji": "🔥🔥", "description": "Бір апта серия! Тамаша!"},
    {"code": "streak_14", "title": "2 апта серия", "emoji": "🔥🔥🔥", "description": "2 апта қатарынан!"},
    {"code": "streak_30", "title": "30 күн серия", "emoji": "👑", "description": "Бір ай! Сен чемпионсың!"},
    {"code": "workouts_10", "title": "10 жаттығу", "emoji": "💪", "description": "10 жаттығу орындадың!"},
    {"code": "workouts_25", "title": "25 жаттығу", "emoji": "💪💪", "description": "25 жаттығу! Жарайсың!"},
    {"code": "workouts_50", "title": "50 жаттығу", "emoji": "🏆", "description": "50 жаттығу - үлкен жетістік!"},
    {"code": "workouts_100", "title": "100 жаттығу", "emoji": "🥇", "description": "100 жаттығу! Керемет!"},
]


async def init_achievements(session: AsyncSession):
    """Инициализировать достижения в БД"""
    for ach_data in ACHIEVEMENTS:
        result = await session.execute(
            select(Achievement).where(Achievement.code == ach_data["code"])
        )
        if not result.scalar_one_or_none():
            achievement = Achievement(
                code=ach_data["code"],
                title=ach_data["title"],
                emoji=ach_data["emoji"],
                description=ach_data["description"]
            )
            session.add(achievement)
    await session.commit()


async def update_streak(session: AsyncSession, user: User) -> dict:
    """
    Обновить streak пользователя после тренировки.
    Возвращает информацию о streak.
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    old_streak = user.current_streak or 0
    
    # Если уже тренировался сегодня - не обновляем
    if user.last_workout_date == today:
        return {
            "streak": user.current_streak,
            "increased": False,
            "new_record": False
        }
    
    # Проверяем, была ли тренировка вчера
    if user.last_workout_date == yesterday:
        # Продолжаем серию
        user.current_streak = (user.current_streak or 0) + 1
    elif user.last_workout_date is None or user.last_workout_date < yesterday:
        # Начинаем новую серию
        user.current_streak = 1
    
    # Обновляем дату последней тренировки
    user.last_workout_date = today
    
    # Проверяем рекорд
    new_record = False
    if user.current_streak > (user.best_streak or 0):
        user.best_streak = user.current_streak
        new_record = True
    
    await session.commit()
    
    return {
        "streak": user.current_streak,
        "increased": user.current_streak > old_streak,
        "new_record": new_record,
        "best": user.best_streak
    }


async def check_and_award_achievements(
    session: AsyncSession, 
    user: User
) -> list[Achievement]:
    """
    Проверить и наградить пользователя достижениями.
    Возвращает список новых достижений.
    """
    new_achievements = []
    
    # Получаем статистику
    total_workouts = await session.execute(
        select(func.count(UserWorkout.id)).where(UserWorkout.user_id == user.id)
    )
    total_count = total_workouts.scalar() or 0
    
    # Определяем какие достижения нужно проверить
    checks = [
        ("first_workout", total_count >= 1),
        ("workouts_10", total_count >= 10),
        ("workouts_25", total_count >= 25),
        ("workouts_50", total_count >= 50),
        ("workouts_100", total_count >= 100),
        ("streak_3", (user.current_streak or 0) >= 3),
        ("streak_7", (user.current_streak or 0) >= 7),
        ("streak_14", (user.current_streak or 0) >= 14),
        ("streak_30", (user.current_streak or 0) >= 30),
    ]
    
    for code, condition in checks:
        if condition:
            # Проверяем, есть ли уже это достижение
            existing = await session.execute(
                select(UserAchievement).join(Achievement).where(
                    UserAchievement.user_id == user.id,
                    Achievement.code == code
                )
            )
            if not existing.scalar_one_or_none():
                # Находим достижение
                ach_result = await session.execute(
                    select(Achievement).where(Achievement.code == code)
                )
                achievement = ach_result.scalar_one_or_none()
                
                if achievement:
                    # Награждаем
                    user_ach = UserAchievement(
                        user_id=user.id,
                        achievement_id=achievement.id
                    )
                    session.add(user_ach)
                    new_achievements.append(achievement)
    
    if new_achievements:
        await session.commit()
    
    return new_achievements


async def get_user_achievements(session: AsyncSession, user_id: int) -> list[dict]:
    """Получить все достижения пользователя"""
    result = await session.execute(
        select(Achievement, UserAchievement.earned_at)
        .join(UserAchievement)
        .where(UserAchievement.user_id == user_id)
        .order_by(UserAchievement.earned_at.desc())
    )
    
    achievements = []
    for ach, earned_at in result:
        achievements.append({
            "code": ach.code,
            "title": ach.title,
            "emoji": ach.emoji,
            "description": ach.description,
            "earned_at": earned_at
        })
    
    return achievements


async def format_achievements_text(achievements: list[dict]) -> str:
    """Форматировать достижения для отображения"""
    if not achievements:
        return "Әзірше жетістіктер жоқ. Жаттығуды бастаңыз! 💪"
    
    text = "🏆 *Менің жетістіктерім:*\n\n"
    for ach in achievements:
        text += f"{ach['emoji']} *{ach['title']}*\n"
        text += f"   _{ach['description']}_\n\n"
    
    return text
