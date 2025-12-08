"""
Обработчики тренировок
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from keyboards import get_workout_actions_keyboard, get_feeling_keyboard, get_main_menu_keyboard
from texts_kk import MENU, WORKOUTS, PROGRESS, ERRORS, AI
from services.users import get_user_by_telegram_id
from services.workouts import (
    get_workout_for_user, 
    mark_workout_completed, 
    get_user_workout_stats
)
from services.ai_service import get_ai_advice
from services.achievements import update_streak, check_and_award_achievements
from utils.formatters import format_workout
from db.session import async_session_maker

router = Router()

# Дни недели на казахском
DAYS_KK = {
    0: "Дүйсенбі",
    1: "Сейсенбі", 
    2: "Сәрсенбі",
    3: "Бейсенбі",
    4: "Жұма",
    5: "Сенбі",
    6: "Жексенбі"
}


def get_workout_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура меню тренировок"""
    today = datetime.now().weekday()
    today_emoji = "📍"
    
    # Все 7 дней недели
    buttons = []
    for i in range(7):
        emoji = today_emoji if i == today else "📅"
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {DAYS_KK[i]}", 
            callback_data=f"workout_day:{i}"
        )])
    
    buttons.append([InlineKeyboardButton(text="📋 Апта жоспары", callback_data="workout:week")])
    buttons.append([InlineKeyboardButton(text="◀️ Артқа", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == MENU["today_workout"])
async def workout_menu(message: Message):
    """Показать меню тренировок"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user or not user.goal:
            await message.answer(ERRORS["no_profile"])
            return
        
        today_index = datetime.now().weekday()
        today_name = DAYS_KK[today_index]
        
        # Показываем недельный план сразу
        text = f"""🏋️ *Апталық жаттығу жоспары*

📍 Бүгін: *{today_name}*

"""
        
        # Собираем план на неделю
        has_workout_today = False
        for day_index in range(7):
            day_name = DAYS_KK[day_index]
            workout = await get_workout_for_user(session, user, day_index)
            
            if day_index == today_index:
                emoji = "➡️"
                has_workout_today = workout is not None
            else:
                emoji = "📅"
            
            if workout:
                # Показываем интенсивность
                intensity = "💪" * (2 if "интенсив" in workout.title.lower() else 1)
                text += f"{emoji} *{day_name}*: {workout.title} {intensity}\n"
            else:
                text += f"{emoji} {day_name}: 😴 Демалыс\n"
        
        text += "\n💡 3 жаттығу/апта - оңтайлы жүктеме!\n"
        
        # Кнопки
        if has_workout_today:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏋️ Бүгінгі жаттығуды бастау", callback_data=f"workout_day:{today_index}")],
                [InlineKeyboardButton(text="📅 Басқа күн таңдау", callback_data="workout:select_day")],
                [InlineKeyboardButton(text="◀️ Артқа", callback_data="back_to_menu")]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📅 Басқа күн таңдау", callback_data="workout:select_day")],
                [InlineKeyboardButton(text="◀️ Артқа", callback_data="back_to_menu")]
            ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "workout:select_day")
async def show_day_selection(callback: CallbackQuery):
    """Показать выбор дня"""
    today_index = datetime.now().weekday()
    today_name = DAYS_KK[today_index]
    
    text = f"""📅 *Күн таңдау*

📍 Бүгін: {today_name}

Жаттығуды қарау үшін күнді таңдаңыз:"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_workout_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("workout_day:"))
async def show_workout_for_day(callback: CallbackQuery):
    """Показать тренировку для выбранного дня"""
    day_index = int(callback.data.split(":")[1])
    day_name = DAYS_KK[day_index]
    today_index = datetime.now().weekday()
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("Профиль табылмады", show_alert=True)
            return
        
        workout = await get_workout_for_user(session, user, day_index)
        
        if workout:
            # Считаем количество упражнений
            exercises_count = len(workout.exercises_json)
            
            workout_text = f"""📅 *{day_name}*

🏋️ *{workout.title}*
📋 Жаттығулар: {exercises_count}

{format_workout({"title": workout.title, "exercises": workout.exercises_json})}
"""
            
            # Кнопки зависят от дня
            if day_index == today_index:
                buttons = [
                    [InlineKeyboardButton(text="✅ Орындадым", callback_data=f"complete:{workout.id}")],
                    [InlineKeyboardButton(text="📅 Басқа күн", callback_data="workout:select_day")],
                    [InlineKeyboardButton(text="◀️ Басты мәзір", callback_data="back_to_menu")]
                ]
            else:
                buttons = [
                    [InlineKeyboardButton(text="📅 Басқа күн", callback_data="workout:select_day")],
                    [InlineKeyboardButton(text="◀️ Басты мәзір", callback_data="back_to_menu")]
                ]
            
            await callback.message.edit_text(
                workout_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
                parse_mode="Markdown"
            )
        else:
            # Профессиональное сообщение об отдыхе
            next_workout = _get_next_workout_day(day_index)
            rest_text = f"""😴 *{day_name} - Демалыс күні*

✨ Бұл жоспарланған демалыс!

Демалыс күндері өте маңызды:
• Бұлшық еттер қалпына келеді
• Күш артады
• Жарақаттан сақтайды

💡 Ұсыныстар:
• Жеңіл серуен
• Созылу жаттығулары
• Жақсы ұйықтау

📅 Келесі жаттығу: {next_workout}"""
            
            await callback.message.edit_text(
                rest_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📅 Басқа күн", callback_data="workout:select_day")],
                    [InlineKeyboardButton(text="◀️ Басты мәзір", callback_data="back_to_menu")]
                ]),
                parse_mode="Markdown"
            )
    
    await callback.answer()


def _get_next_workout_day(current_day: int) -> str:
    """Получить следующий день тренировки"""
    # Стандартный план: Пн(0), Ср(2), Пт(4)
    workout_days = [0, 2, 4]
    
    for offset in range(1, 8):
        next_day = (current_day + offset) % 7
        if next_day in workout_days:
            return DAYS_KK[next_day]
    
    return "Дүйсенбі"


@router.callback_query(F.data == "workout:week")
async def show_week_plan(callback: CallbackQuery):
    """Показать план на неделю"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("Профиль табылмады", show_alert=True)
            return
        
        text = "📋 Апта жоспары:\n\n"
        
        for day_index in range(7):
            day_name = DAYS_KK[day_index]
            workout = await get_workout_for_user(session, user, day_index)
            
            if workout:
                text += f"📅 {day_name}: {workout.title}\n"
            else:
                text += f"😴 {day_name}: Демалыс\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Артқа", callback_data="workout:select_day")]
            ])
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("complete:"))
async def complete_workout(callback: CallbackQuery):
    """Отметить тренировку как выполненную"""
    workout_id = int(callback.data.split(":")[1])
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        WORKOUTS["workout_completed"],
        reply_markup=get_feeling_keyboard(workout_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("feeling:"))
async def process_feeling(callback: CallbackQuery):
    """Обработка оценки самочувствия"""
    parts = callback.data.split(":")
    workout_id = int(parts[1])
    feeling = parts[2]
    
    streak_info = None
    new_achievements = []
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("Профиль табылмады", show_alert=True)
            return
        
        # Сохраняем выполненную тренировку
        user_workout = await mark_workout_completed(
            session,
            user.id,
            workout_id,
            feeling=feeling
        )
        
        # Обновляем streak
        streak_info = await update_streak(session, user)
        
        # Проверяем достижения
        new_achievements = await check_and_award_achievements(session, user)
        
        # Получаем название тренировки для AI
        from db.models import Workout
        workout = await session.get(Workout, workout_id)
        workout_title = workout.title if workout else "Жаттығу"
        
        # Формируем профиль для AI
        user_profile = {
            "gender": user.gender,
            "age": user.age,
            "goal": user.goal,
            "level": user.level
        }
    
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Формируем сообщение о streak
    streak_text = ""
    if streak_info and streak_info.get("streak", 0) > 0:
        streak = streak_info["streak"]
        fire = "🔥" * min(streak, 5)
        streak_text = f"\n\n{fire} *Серия: {streak} күн!*"
        
        if streak_info.get("new_record"):
            streak_text += " 🏆 Жаңа рекорд!"
    
    # Формируем сообщение о достижениях
    achievements_text = ""
    if new_achievements:
        achievements_text = "\n\n🎉 *Жаңа жетістіктер:*\n"
        for ach in new_achievements:
            achievements_text += f"  {ach.emoji} {ach.title}\n"
    
    # Отправляем базовый ответ
    await callback.message.answer(
        WORKOUTS["thanks_feedback"] + streak_text + achievements_text,
        parse_mode="Markdown"
    )
    
    # Получаем AI-совет (асинхронно)
    try:
        ai_advice = await get_ai_advice(user_profile, workout_title, feeling)
        await callback.message.answer(
            AI["ai_advice"].format(advice=ai_advice),
            reply_markup=get_main_menu_keyboard()
        )
    except Exception:
        # Если AI недоступен, просто показываем меню
        await callback.message.answer(
            "💪 Жалғастыра беріңіз!",
            reply_markup=get_main_menu_keyboard()
        )
    
    await callback.answer()


@router.callback_query(F.data == "skip")
async def skip_workout(callback: CallbackQuery):
    """Пропустить тренировку"""
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Жақсы! Кейінірек орындай аласыз 💪",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.message(F.text == MENU["my_progress"])
async def show_progress(message: Message):
    """Показать прогресс пользователя"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer(ERRORS["no_profile"])
            return
        
        # Получаем статистику
        stats = await get_user_workout_stats(session, user.id, days=30)
        
        if stats["total"] == 0:
            await message.answer(
                PROGRESS["no_workouts"],
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏋️ Жаттығуға бастау", callback_data="workout:menu")],
                    [InlineKeyboardButton(text="◀️ Артқа", callback_data="back_to_menu")]
                ])
            )
            return
        
        # Форматируем статистику
        feeling_map = {
            "easy": "😊 Жеңіл",
            "normal": "💪 Қалыпты",
            "hard": "😅 Қиын",
            None: "—"
        }
        
        avg_feeling_text = feeling_map.get(stats["average_feeling"], "—")
        
        # Визуальный прогресс бар
        progress_percent = min(stats["last_7_days"] / 4 * 100, 100)
        filled = int(progress_percent / 10)
        bar = "🟩" * filled + "⬜" * (10 - filled)
        
        # Streak info
        current_streak = user.current_streak or 0
        best_streak = user.best_streak or 0
        fire = "🔥" * min(current_streak, 5) if current_streak > 0 else ""
        
        progress_text = f"""📊 *Менің нәтижелерім*

{fire} *Серия: {current_streak} күн*
🏆 Рекорд: {best_streak} күн

📅 Соңғы 7 күн: {stats["last_7_days"]} жаттығу
📆 Соңғы 30 күн: {stats["last_30_days"]} жаттығу
🎯 Барлығы: {stats["total"]} жаттығу

{bar} {progress_percent:.0f}%
_Мақсат: 4 жаттығу/апта_

😊 Орташа сезім: {avg_feeling_text}

💪 Жалғастыра беріңіз!
"""
        
        await message.answer(
            progress_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏆 Жетістіктерім", callback_data="achievements")],
                [InlineKeyboardButton(text="📜 Тарих", callback_data="workout:history")],
                [InlineKeyboardButton(text="🏋️ Жаттығуға", callback_data="workout:menu")],
                [InlineKeyboardButton(text="◀️ Артқа", callback_data="back_to_menu")]
            ])
        )


@router.callback_query(F.data == "achievements")
async def show_achievements(callback: CallbackQuery):
    """Показать достижения пользователя"""
    from services.achievements import get_user_achievements, format_achievements_text
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("Профиль табылмады", show_alert=True)
            return
        
        achievements = await get_user_achievements(session, user.id)
        text = await format_achievements_text(achievements)
        
        # Показываем количество достижений
        total_achievements = 9  # Всего достижений в системе
        earned_count = len(achievements)
        
        header = f"🏆 *Жетістіктер: {earned_count}/{total_achievements}*\n\n"
        
        await callback.message.edit_text(
            header + text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Нәтижелерге", callback_data="progress")],
                [InlineKeyboardButton(text="◀️ Артқа", callback_data="back_to_menu")]
            ])
        )
    
    await callback.answer()


@router.callback_query(F.data == "workout:history")
async def show_workout_history(callback: CallbackQuery):
    """Показать историю тренировок за последние 30 дней"""
    from sqlalchemy import select
    from db.models import UserWorkout, Workout
    from datetime import date, timedelta
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("Профиль табылмады", show_alert=True)
            return
        
        # Получаем тренировки за 30 дней
        start_date = date.today() - timedelta(days=30)
        result = await session.execute(
            select(UserWorkout, Workout)
            .join(Workout)
            .where(
                UserWorkout.user_id == user.id,
                UserWorkout.date >= start_date
            )
            .order_by(UserWorkout.date.desc())
            .limit(15)
        )
        
        workouts = result.all()
        
        if not workouts:
            text = "📜 *Тарих*\n\nСоңғы 30 күнде жаттығу жоқ."
        else:
            text = "📜 *Соңғы жаттығулар:*\n\n"
            
            for uw, w in workouts:
                feeling_emoji = {"easy": "😊", "normal": "💪", "hard": "😅"}.get(uw.feeling, "")
                text += f"📅 *{uw.date.strftime('%d.%m')}* - {w.title} {feeling_emoji}\n"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Нәтижелерге", callback_data="progress")],
                [InlineKeyboardButton(text="◀️ Артқа", callback_data="back_to_menu")]
            ])
        )
    
    await callback.answer()


@router.callback_query(F.data == "progress")
async def back_to_progress(callback: CallbackQuery):
    """Вернуться к прогрессу через callback"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("Профиль табылмады", show_alert=True)
            return
        
        stats = await get_user_workout_stats(session, user.id, days=30)
        
        feeling_map = {
            "easy": "😊 Жеңіл",
            "normal": "💪 Қалыпты", 
            "hard": "😅 Қиын",
            None: "—"
        }
        
        avg_feeling_text = feeling_map.get(stats["average_feeling"], "—")
        progress_percent = min(stats["last_7_days"] / 4 * 100, 100)
        filled = int(progress_percent / 10)
        bar = "🟩" * filled + "⬜" * (10 - filled)
        
        current_streak = user.current_streak or 0
        best_streak = user.best_streak or 0
        fire = "🔥" * min(current_streak, 5) if current_streak > 0 else ""
        
        progress_text = f"""📊 *Менің нәтижелерім*

{fire} *Серия: {current_streak} күн*
🏆 Рекорд: {best_streak} күн

📅 Соңғы 7 күн: {stats["last_7_days"]} жаттығу
📆 Соңғы 30 күн: {stats["last_30_days"]} жаттығу
🎯 Барлығы: {stats["total"]} жаттығу

{bar} {progress_percent:.0f}%

💪 Жалғастыра беріңіз!
"""
        
        await callback.message.edit_text(
            progress_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏆 Жетістіктерім", callback_data="achievements")],
                [InlineKeyboardButton(text="📜 Тарих", callback_data="workout:history")],
                [InlineKeyboardButton(text="🏋️ Жаттығуға", callback_data="workout:menu")],
                [InlineKeyboardButton(text="◀️ Артқа", callback_data="back_to_menu")]
            ])
        )
    
    await callback.answer()
