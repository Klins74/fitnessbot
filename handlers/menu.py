"""
Обработчики главного меню
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from keyboards import get_main_menu_keyboard, get_reminders_keyboard, get_days_selection_keyboard
from texts_kk import MENU, REMINDERS, BUTTONS
from services.users import get_user_by_telegram_id, update_reminder_settings
from utils.validators import validate_time
from db.session import async_session_maker
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()


class ReminderStates(StatesGroup):
    """Состояния для настройки напоминаний"""
    waiting_for_time = State()
    selecting_days = State()


@router.message(F.text == MENU["main_menu"])
async def show_main_menu(message: Message):
    """Показать главное меню"""
    await message.answer(
        "📱 Басты мәзір",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == MENU["edit_plan"])
async def edit_plan(message: Message, state: FSMContext):
    """Изменить план тренировок (перезапуск онбординга)"""
    from handlers.onboarding import start_onboarding
    await start_onboarding(message, state)


@router.message(F.text == MENU["reminders"])
async def reminders_menu(message: Message):
    """Меню настройки напоминаний"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("Сначала заполните профиль: /start")
            return
        
        enabled = user.reminder_enabled
        time_info = f"\n\nТекущее время: {user.reminder_time}" if user.reminder_time else ""
        
        await message.answer(
            REMINDERS["settings"] + time_info,
            reply_markup=get_reminders_keyboard(enabled)
        )


@router.callback_query(F.data.startswith("reminder:"))
async def handle_reminder_action(callback: CallbackQuery, state: FSMContext):
    """Обработка действий с напоминаниями"""
    action = callback.data.split(":")[1]
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("Профиль не найден", show_alert=True)
            return
        
        if action == "enable":
            # Просим выбрать дни недели
            await state.set_state(ReminderStates.selecting_days)
            await state.update_data(selected_days=[])
            
            await callback.message.edit_text(
                REMINDERS["choose_days"],
                reply_markup=get_days_selection_keyboard([])
            )
        
        elif action == "disable":
            await update_reminder_settings(session, callback.from_user.id, False)
            await callback.message.edit_text(
                REMINDERS["disabled"],
                reply_markup=None
            )
            await callback.message.answer(
                "✅ Готово",
                reply_markup=get_main_menu_keyboard()
            )
        
        await callback.answer()


@router.callback_query(F.data.startswith("day_toggle:"))
async def toggle_day_selection(callback: CallbackQuery, state: FSMContext):
    """Переключение выбора дня недели"""
    day = callback.data.split(":")[1]
    
    data = await state.get_data()
    selected_days = data.get("selected_days", [])
    
    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)
    
    await state.update_data(selected_days=selected_days)
    
    await callback.message.edit_reply_markup(
        reply_markup=get_days_selection_keyboard(selected_days)
    )
    await callback.answer()


@router.callback_query(F.data == "days_confirm")
async def confirm_days_selection(callback: CallbackQuery, state: FSMContext):
    """Подтверждение выбора дней"""
    data = await state.get_data()
    selected_days = data.get("selected_days", [])
    
    if not selected_days:
        await callback.answer("Выберите хотя бы один день!", show_alert=True)
        return
    
    # Сохраняем выбранные дни и переходим к выбору времени
    await state.set_state(ReminderStates.waiting_for_time)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(REMINDERS["choose_time"])
    await callback.answer()


@router.message(ReminderStates.waiting_for_time)
async def process_reminder_time(message: Message, state: FSMContext):
    """Обработка ввода времени напоминания"""
    is_valid, time_str, error = validate_time(message.text)
    
    if not is_valid:
        await message.answer(error)
        return
    
    # Получаем выбранные дни
    data = await state.get_data()
    selected_days = data.get("selected_days", [])
    
    async with async_session_maker() as session:
        await update_reminder_settings(
            session, 
            message.from_user.id, 
            True, 
            time_str,
            selected_days
        )
    
    await state.clear()
    
    # Форматируем список дней на казахском
    from texts_kk import REMINDERS
    days_names = [REMINDERS["weekdays"][day] for day in selected_days]
    days_text = ", ".join(days_names)
    
    await message.answer(
        f"⏰ Еске салғыш орнатылды!\n"
        f"Уақыт: {time_str}\n"
        f"Күндер: {days_text}",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Вернуться в главное меню"""
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "📱 Басты мәзір",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
