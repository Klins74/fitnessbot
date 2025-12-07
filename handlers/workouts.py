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
    
    buttons = [
        [InlineKeyboardButton(
            text=f"{today_emoji if i == today else '📅'} {DAYS_KK[i]}", 
            callback_data=f"workout_day:{i}"
        )]
        for i in [0, 2, 4, 6]  # Пн, Ср, Пт, Вс
    ]
    
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
        
        # Получаем тренировку на сегодня
        workout = await get_workout_for_user(session, user, today_index)
        
        if workout:
            workout_text = f"""🏋️ Бүгін: {today_name}

📝 Жаттығу: {workout.title}

{format_workout({"title": workout.title, "exercises": workout.exercises_json})}
"""
            await message.answer(
                workout_text,
                reply_markup=get_workout_actions_keyboard(workout.id)
            )
        else:
            # Показываем меню выбора дня
            text = f"""🏋️ Жаттығулар

📍 Бүгін: {today_name}

Бүгін демалыс күні! 
Басқа күнді таңдап, жаттығуды қарай аласыз:"""
            
            await message.answer(text, reply_markup=get_workout_menu_keyboard())


@router.callback_query(F.data.startswith("workout_day:"))
async def show_workout_for_day(callback: CallbackQuery):
    """Показать тренировку для выбранного дня"""
    day_index = int(callback.data.split(":")[1])
    day_name = DAYS_KK[day_index]
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("Профиль табылмады", show_alert=True)
            return
        
        workout = await get_workout_for_user(session, user, day_index)
        
        if workout:
            workout_text = f"""📅 {day_name}

📝 Жаттығу: {workout.title}

{format_workout({"title": workout.title, "exercises": workout.exercises_json})}
"""
            await callback.message.edit_text(
                workout_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Орындадым", callback_data=f"complete:{workout.id}")],
                    [InlineKeyboardButton(text="◀️ Артқа", callback_data="workout:menu")]
                ])
            )
        else:
            await callback.message.edit_text(
                f"📅 {day_name}\n\nБұл күні демалыс 😊",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="◀️ Артқа", callback_data="workout:menu")]
                ])
            )
    
    await callback.answer()


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
                [InlineKeyboardButton(text="◀️ Артқа", callback_data="workout:menu")]
            ])
        )
    
    await callback.answer()


@router.callback_query(F.data == "workout:menu")
async def back_to_workout_menu(callback: CallbackQuery):
    """Вернуться в меню тренировок"""
    today_index = datetime.now().weekday()
    today_name = DAYS_KK[today_index]
    
    text = f"""🏋️ Жаттығулар

📍 Бүгін: {today_name}

Күнді таңдаңыз:"""
    
    await callback.message.edit_text(text, reply_markup=get_workout_menu_keyboard())
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
    
    # Отправляем базовый ответ
    await callback.message.answer(WORKOUTS["thanks_feedback"])
    
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
        
        progress_text = f"""📊 Менің нәтижелерім

🏆 Барлығы: {stats["total"]} жаттығу
📅 Соңғы 7 күн: {stats["last_7_days"]} жаттығу
📆 Соңғы 30 күн: {stats["last_30_days"]} жаттығу

{bar} {progress_percent:.0f}%
Мақсат: 4 жаттығу/апта

😊 Орташа сезім: {avg_feeling_text}

💪 Жалғастыра беріңіз!
"""
        
        await message.answer(
            progress_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏋️ Жаттығуға", callback_data="workout:menu")],
                [InlineKeyboardButton(text="◀️ Артқа", callback_data="back_to_menu")]
            ])
        )
