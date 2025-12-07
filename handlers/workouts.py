"""
Обработчики тренировок
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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


@router.message(F.text == MENU["today_workout"])
async def today_workout(message: Message):
    """Показать тренировку на сегодня"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user or not user.goal:
            await message.answer(ERRORS["no_profile"])
            return
        
        # Определяем день недели (0 = понедельник, 6 = воскресенье)
        today_index = datetime.now().weekday()
        
        # Получаем тренировку
        workout = await get_workout_for_user(session, user, today_index)
        
        if not workout:
            await message.answer(WORKOUTS["no_workout_today"])
            return
        
        # Форматируем и отправляем тренировку
        workout_dict = {
            "title": workout.title,
            "exercises": workout.exercises_json
        }
        
        workout_text = format_workout(workout_dict)
        
        await message.answer(
            workout_text,
            reply_markup=get_workout_actions_keyboard(workout.id)
        )


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
            await callback.answer("Профиль не найден", show_alert=True)
            return
        
        # Сохраняем выполненную тренировку
        user_workout = await mark_workout_completed(
            session,
            user.id,
            workout_id,
            feeling=feeling
        )
        
        # Получаем название тренировки для AI
        workout = await session.get(
            __import__('db.models', fromlist=['Workout']).Workout, 
            workout_id
        )
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
        "Добре! Тренировку можно выполнить позже.",
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
            await message.answer(PROGRESS["no_workouts"])
            return
        
        # Форматируем статистику
        feeling_map = {
            "easy": WORKOUTS["feeling_easy"],
            "normal": WORKOUTS["feeling_normal"],
            "hard": WORKOUTS["feeling_hard"],
            None: "—"
        }
        
        avg_feeling_text = feeling_map.get(stats["average_feeling"], "—")
        
        progress_text = (
            PROGRESS["stats_title"] +
            PROGRESS["total_workouts"].format(count=stats["total"]) +
            PROGRESS["last_7_days"].format(count=stats["last_7_days"]) +
            PROGRESS["last_30_days"].format(count=stats["last_30_days"]) +
            PROGRESS["average_feeling"].format(feeling=avg_feeling_text)
        )
        
        await message.answer(progress_text)
