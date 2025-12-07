"""
Обработчики онбординга
"""
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.states import OnboardingStates
from keyboards import (
    get_start_keyboard, get_gender_keyboard, get_goals_keyboard,
    get_levels_keyboard, get_workout_types_keyboard, get_confirm_keyboard,
    get_main_menu_keyboard
)
from texts_kk import ONBOARDING, BUTTONS
from utils.validators import validate_age, validate_height, validate_weight
from utils.formatters import format_profile
from services.users import get_user_by_telegram_id, create_user, update_user
from db.session import async_session_maker

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    # Проверяем, есть ли уже профиль
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
    
    if user and user.goal:
        # Пользователь уже зарегистрирован
        await message.answer(
            "Сәлеметсіз бе! Сіз қайта қош келдіңіз! 👋",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # Новый пользователь - начинаем онбординг
        await message.answer(
            ONBOARDING["welcome"],
            reply_markup=get_start_keyboard()
        )


@router.message(F.text == BUTTONS["start"])
async def start_onboarding(message: Message, state: FSMContext):
    """Начало онбординга"""
    await state.set_state(OnboardingStates.gender)
    await message.answer(
        ONBOARDING["ask_gender"],
        reply_markup=get_gender_keyboard()
    )


@router.callback_query(StateFilter(OnboardingStates.gender), F.data.startswith("gender:"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора пола"""
    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    await state.set_state(OnboardingStates.age)
    
    await callback.message.edit_text(ONBOARDING["ask_gender"] + f" {gender}")
    await callback.message.answer(ONBOARDING["ask_age"])
    await callback.answer()


@router.message(StateFilter(OnboardingStates.age))
async def process_age(message: Message, state: FSMContext):
    """Обработка ввода возраста"""
    is_valid, age, error = validate_age(message.text)
    
    if not is_valid:
        await message.answer(error)
        return
    
    await state.update_data(age=age)
    await state.set_state(OnboardingStates.height)
    await message.answer(ONBOARDING["ask_height"])


@router.message(StateFilter(OnboardingStates.height))
async def process_height(message: Message, state: FSMContext):
    """Обработка ввода роста"""
    is_valid, height, error = validate_height(message.text)
    
    if not is_valid:
        await message.answer(error)
        return
    
    await state.update_data(height=height)
    await state.set_state(OnboardingStates.weight)
    await message.answer(ONBOARDING["ask_weight"])


@router.message(StateFilter(OnboardingStates.weight))
async def process_weight(message: Message, state: FSMContext):
    """Обработка ввода веса"""
    is_valid, weight, error = validate_weight(message.text)
    
    if not is_valid:
        await message.answer(error)
        return
    
    await state.update_data(weight=weight)
    await state.set_state(OnboardingStates.goal)
    await message.answer(
        ONBOARDING["ask_goal"],
        reply_markup=get_goals_keyboard()
    )


@router.callback_query(StateFilter(OnboardingStates.goal), F.data.startswith("goal:"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора цели"""
    goal = callback.data.split(":")[1]
    await state.update_data(goal=goal)
    await state.set_state(OnboardingStates.level)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        ONBOARDING["ask_level"],
        reply_markup=get_levels_keyboard()
    )
    await callback.answer()


@router.callback_query(StateFilter(OnboardingStates.level), F.data.startswith("level:"))
async def process_level(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора уровня"""
    level = callback.data.split(":")[1]
    await state.update_data(level=level)
    await state.set_state(OnboardingStates.workout_type)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        ONBOARDING["ask_workout_type"],
        reply_markup=get_workout_types_keyboard()
    )
    await callback.answer()


@router.callback_query(StateFilter(OnboardingStates.workout_type), F.data.startswith("workout_type:"))
async def process_workout_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа тренировок"""
    workout_type = callback.data.split(":")[1]
    await state.update_data(workout_type=workout_type)
    await state.set_state(OnboardingStates.confirm)
    
    # Показываем сводку для подтверждения
    user_data = await state.get_data()
    profile_text = format_profile(user_data)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        profile_text,
        reply_markup=get_confirm_keyboard()
    )
    await callback.answer()


@router.callback_query(StateFilter(OnboardingStates.confirm), F.data.startswith("confirm:"))
async def process_confirm(callback: CallbackQuery, state: FSMContext):
    """Обработка подтверждения профиля"""
    action = callback.data.split(":")[1]
    
    if action == "yes":
        # Сохраняем профиль в БД
        user_data = await state.get_data()
        
        async with async_session_maker() as session:
            existing_user = await get_user_by_telegram_id(session, callback.from_user.id)
            
            if existing_user:
                await update_user(session, callback.from_user.id, user_data)
            else:
                await create_user(session, callback.from_user.id, user_data)
        
        await state.clear()
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            ONBOARDING["profile_saved"],
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # Повторить онбординг
        await state.clear()
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            ONBOARDING["profile_cancelled"]
        )
    
    await callback.answer()
