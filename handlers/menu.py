"""
Обработчики главного меню
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from keyboards import get_main_menu_keyboard, get_reminders_keyboard
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
            # Просим ввести время
            await state.set_state(ReminderStates.waiting_for_time)
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.message.answer(REMINDERS["choose_time"])
        
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


@router.message(ReminderStates.waiting_for_time)
async def process_reminder_time(message: Message, state: FSMContext):
    """Обработка ввода времени напоминания"""
    is_valid, time_str, error = validate_time(message.text)
    
    if not is_valid:
        await message.answer(error)
        return
    
    async with async_session_maker() as session:
        await update_reminder_settings(
            session, 
            message.from_user.id, 
            True, 
            time_str
        )
    
    await state.clear()
    await message.answer(
        REMINDERS["time_set"].format(time=time_str),
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
