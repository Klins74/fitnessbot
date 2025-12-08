"""
Обработчики AI функций
"""
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_main_menu_keyboard
from texts_kk import MENU, AI, ERRORS
from services.users import get_user_by_telegram_id
from services.ai_service import ask_ai_trainer
from nutrition_kk import get_nutrition_for_goal, get_all_recipes, NUTRITION_TIPS
from db.session import async_session_maker

router = Router()


class AIStates(StatesGroup):
    """Состояния для AI-тренера"""
    waiting_for_question = State()


def get_nutrition_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура раздела питания"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мәзір үлгісі", callback_data="nutrition:menu")],
        [InlineKeyboardButton(text="📖 Рецепттер", callback_data="nutrition:recipes")],
        [InlineKeyboardButton(text="🤖 AI кеңесі", callback_data="nutrition:ai")],
        [InlineKeyboardButton(text="◀️ Артқа", callback_data="nutrition:back")],
    ])


@router.message(F.text == MENU["ai_trainer"])
async def ai_trainer_menu(message: Message, state: FSMContext):
    """Открыть AI тренера"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer(ERRORS["no_profile"])
            return
    
    await state.set_state(AIStates.waiting_for_question)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Басты мәзірге оралу", callback_data="ai:back")]
    ])
    
    await message.answer(
        AI["trainer_greeting"],
        reply_markup=keyboard
    )


@router.message(AIStates.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext):
    """Обработка вопроса к AI"""
    # Проверяем, не нажал ли пользователь кнопку меню
    if message.text in [MENU["today_workout"], MENU["my_progress"], MENU["edit_plan"], 
                        MENU["reminders"], MENU["nutrition"], MENU["main_menu"], 
                        MENU["video_workouts"], MENU["contacts"]]:
        await state.clear()
        return
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await state.clear()
            await message.answer(ERRORS["no_profile"])
            return
        
        # Показываем, что обрабатываем
        loading_msg = await message.answer(AI["ai_loading"])
        
        # Формируем профиль для AI
        user_profile = {
            "age": user.age,
            "goal": user.goal,
            "level": user.level,
            "gender": user.gender
        }
        
        # Получаем ответ от AI
        answer = await ask_ai_trainer(message.text, user_profile)
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Кнопка для продолжения диалога или выхода
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Басты мәзірге оралу", callback_data="ai:back")]
        ])
        
        await message.answer(
            AI["ai_advice"].format(advice=answer),
            reply_markup=keyboard
        )
    
    # НЕ очищаем state - остаёмся в режиме диалога!


@router.message(F.text == MENU["nutrition"])
async def nutrition_menu(message: Message):
    """Открыть раздел питания"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer(ERRORS["no_profile"])
            return
        
        # Получаем советы для цели пользователя
        nutrition_data = NUTRITION_TIPS.get(user.goal, NUTRITION_TIPS["stay_fit"])
        tips_text = "\n".join(nutrition_data["tips"])
        
        text = f"""
{nutrition_data["title"]}

{tips_text}

👇 Толық ақпарат алу үшін таңдаңыз:
"""
        await message.answer(text.strip(), reply_markup=get_nutrition_keyboard())


@router.callback_query(F.data.startswith("nutrition:"))
async def handle_nutrition_action(callback: CallbackQuery):
    """Обработка действий раздела питания"""
    action = callback.data.split(":")[1]
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("Профиль табылмады", show_alert=True)
            return
        
        if action == "menu":
            # Показать пример меню
            nutrition_data = NUTRITION_TIPS.get(user.goal, NUTRITION_TIPS["stay_fit"])
            await callback.message.answer(
                nutrition_data["meal_example"],
                reply_markup=get_main_menu_keyboard()
            )
            
        elif action == "recipes":
            # Показать рецепты
            recipes = get_all_recipes()
            await callback.message.answer(
                recipes,
                reply_markup=get_main_menu_keyboard()
            )
            
        elif action == "ai":
            # AI совет
            from services.ai_service import get_nutrition_advice
            
            loading_msg = await callback.message.answer("🤖 AI кеңесін дайындап жатырмын...")
            
            user_profile = {
                "weight_kg": user.weight_kg,
                "height_cm": user.height_cm,
                "goal": user.goal,
                "gender": user.gender
            }
            
            advice = await get_nutrition_advice(user_profile)
            await loading_msg.delete()
            await callback.message.answer(
                f"🤖 AI тамақтану кеңесі:\n\n{advice}",
                reply_markup=get_main_menu_keyboard()
            )
            
        elif action == "back":
            await callback.message.answer(
                "📱 Басты мәзір",
                reply_markup=get_main_menu_keyboard()
            )
    
    await callback.answer()


@router.callback_query(F.data == "ai:back")
async def ai_back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню из AI раздела"""
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "📱 Басты мәзір",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
