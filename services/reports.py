"""
Сервис для отчетов и улучшенных напоминаний
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, UserWorkout
from datetime import date, timedelta


async def generate_weekly_report(session: AsyncSession, user: User) -> str:
    """Генерировать недельный отчет для пользователя"""
    
    # Статистика за эту неделю
    week_start = date.today() - timedelta(days=7)
    result = await session.execute(
        select(func.count(UserWorkout.id)).where(
            UserWorkout.user_id == user.id,
            UserWorkout.date >= week_start
        )
    )
    this_week = result.scalar() or 0
    
    # Статистика за прошлую неделю
    prev_week_start = week_start - timedelta(days=7)
    result = await session.execute(
        select(func.count(UserWorkout.id)).where(
            UserWorkout.user_id == user.id,
            UserWorkout.date >= prev_week_start,
            UserWorkout.date < week_start
        )
    )
    last_week = result.scalar() or 0
    
    # Сравнение
    if this_week > last_week:
        comparison = f"📈 Өткен аптадан +{this_week - last_week} жаттығу көп!"
    elif this_week < last_week:
        comparison = f"📉 Өткен аптадан {last_week - this_week} жаттығу аз"
    else:
        comparison = "📊 Өткен аптамен бірдей"
    
    # Streak info
    streak = user.current_streak or 0
    fire = "🔥" * min(streak, 5) if streak > 0 else ""
    
    # Прогресс бар
    goal = 4  # 4 тренировки в неделю
    progress = min(this_week / goal * 100, 100)
    filled = int(progress / 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)
    
    report = f"""📊 *Апталық есеп*

🏋️ Бұл апта: *{this_week} жаттығу*
🎯 Мақсат: {goal} жаттығу

{bar} {progress:.0f}%

{comparison}

{fire} Серия: *{streak} күн*
🏆 Рекорд: {user.best_streak or 0} күн

💪 Келесі апта да жалғастыр!
"""
    
    return report


def get_reminder_message(user: User) -> str:
    """Получить контекстное сообщение напоминания"""
    
    streak = user.current_streak or 0
    goal = user.goal or "stay_fit"
    
    # Базовые сообщения по streak
    if streak == 0:
        messages = [
            "⏰ Жаттығу уақыты келді! Бүгін бастау керек 💪",
            "🌟 Жаңа басталу - жаңа мүмкіндік! Бүгін жаттық!"
        ]
    elif streak < 3:
        messages = [
            f"⏰ Жаттығу уақыты! 🔥 Серия: {streak} күн - жалғастыр!",
            f"💪 Тамаша! {streak} күн серия бар. Бүгін де жалғастыр!"
        ]
    elif streak < 7:
        messages = [
            f"🔥🔥 {streak} күн серия! Аптаға жақындадың - тоқтама!",
            f"⚡ Сен жаттығу машинасысың! {streak} күн серия!"
        ]
    else:
        messages = [
            f"🔥🔥🔥 {streak} күн серия! Сен чемпионсың! Жалғастыр!",
            f"👑 {streak} күн серия - керемет! Тарихыңды жаз!"
        ]
    
    # Добавляем контекст по цели
    goal_texts = {
        "lose_weight": "\n🎯 Салмақ жоғалту мақсатына жақындап жатырсың!",
        "gain_muscle": "\n💪 Бұлшық ет жинау үшін тұрақты жаттығу маңызды!",
        "stay_fit": "\n🏃 Форманы сақтау үшін жалғастыр!"
    }
    
    import random
    message = random.choice(messages)
    
    if goal in goal_texts:
        message += goal_texts[goal]
    
    return message


async def get_users_for_reminder(session: AsyncSession) -> list[User]:
    """Получить пользователей для напоминания в текущее время"""
    from datetime import datetime
    
    current_time = datetime.now().strftime("%H:%M")
    current_day = datetime.now().strftime("%A").lower()
    
    result = await session.execute(
        select(User).where(
            User.reminder_enabled == True,
            User.reminder_time == current_time
        )
    )
    
    users = []
    for user in result.scalars():
        # Проверяем день недели
        if user.reminder_days:
            if current_day in user.reminder_days:
                users.append(user)
        else:
            # Если дни не выбраны - напоминаем каждый день
            users.append(user)
    
    return users
