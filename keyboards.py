"""
Клавиатуры для бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from texts_kk import BUTTONS, GENDERS, GOALS, LEVELS, WORKOUT_TYPES, MENU, WORKOUTS, REMINDERS


def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для начала работы"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BUTTONS["start"])]],
        resize_keyboard=True
    )
    return keyboard


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора пола"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=GENDERS["male"], callback_data="gender:male")],
        [InlineKeyboardButton(text=GENDERS["female"], callback_data="gender:female")]
    ])
    return keyboard


def get_goals_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора целей"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=GOALS["lose_weight"], callback_data="goal:lose_weight")],
        [InlineKeyboardButton(text=GOALS["gain_muscle"], callback_data="goal:gain_muscle")],
        [InlineKeyboardButton(text=GOALS["stay_fit"], callback_data="goal:stay_fit")]
    ])
    return keyboard


def get_levels_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора уровня"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEVELS["beginner"], callback_data="level:beginner")],
        [InlineKeyboardButton(text=LEVELS["intermediate"], callback_data="level:intermediate")]
    ])
    return keyboard


def get_workout_types_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа тренировок"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=WORKOUT_TYPES["home"], callback_data="workout_type:home")],
        [InlineKeyboardButton(text=WORKOUT_TYPES["gym"], callback_data="workout_type:gym")]
    ])
    return keyboard


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения профиля"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTONS["yes"], callback_data="confirm:yes")],
        [InlineKeyboardButton(text=BUTTONS["change"], callback_data="confirm:no")]
    ])
    return keyboard


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU["today_workout"])],
            [KeyboardButton(text=MENU["my_progress"])],
            [KeyboardButton(text=MENU["video_workouts"])],
            [KeyboardButton(text=MENU["ai_trainer"]), KeyboardButton(text=MENU["nutrition"])],
            [KeyboardButton(text=MENU["reminders"]), KeyboardButton(text=MENU["contacts"])],
            [KeyboardButton(text=MENU["edit_plan"])]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_workout_actions_keyboard(workout_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с тренировкой"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=WORKOUTS["completed_button"], callback_data=f"complete:{workout_id}")],
        [InlineKeyboardButton(text=WORKOUTS["skip_button"], callback_data="skip")],
        [InlineKeyboardButton(text=BUTTONS["back"], callback_data="back_to_menu")]
    ])
    return keyboard


def get_feeling_keyboard(workout_id: int) -> InlineKeyboardMarkup:
    """Клавиатура оценки самочувствия после тренировки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=WORKOUTS["feeling_easy"], callback_data=f"feeling:{workout_id}:easy")],
        [InlineKeyboardButton(text=WORKOUTS["feeling_normal"], callback_data=f"feeling:{workout_id}:normal")],
        [InlineKeyboardButton(text=WORKOUTS["feeling_hard"], callback_data=f"feeling:{workout_id}:hard")]
    ])
    return keyboard


def get_reminders_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    """Клавиатура настройки напоминаний"""
    action = "disable" if enabled else "enable"
    text = BUTTONS["disable"] if enabled else BUTTONS["enable"]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=f"reminder:{action}")],
        [InlineKeyboardButton(text=BUTTONS["back"], callback_data="back_to_menu")]
    ])
    return keyboard


def get_video_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категорий видео"""
    from texts_kk import VIDEO_WORKOUTS
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=VIDEO_WORKOUTS["categories"]["strength"], 
            callback_data="video_cat:strength"
        )],
        [InlineKeyboardButton(
            text=VIDEO_WORKOUTS["categories"]["cardio"], 
            callback_data="video_cat:cardio"
        )],
        [InlineKeyboardButton(
            text=VIDEO_WORKOUTS["categories"]["stretching"], 
            callback_data="video_cat:stretching"
        )],
        [InlineKeyboardButton(text=BUTTONS["back"], callback_data="back_to_menu")]
    ])
    return keyboard


def get_video_list_keyboard(category: str) -> InlineKeyboardMarkup:
    """Клавиатура со списком видео в категории"""
    from texts_kk import VIDEO_WORKOUTS
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=VIDEO_WORKOUTS["back_to_categories"], 
            callback_data="video_categories"
        )]
    ])
    return keyboard


def get_days_selection_keyboard(selected_days: list = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора дней недели для напоминаний"""
    from texts_kk import REMINDERS
    
    if selected_days is None:
        selected_days = []
    
    days_map = {
        "monday": "Пн",
        "tuesday": "Вт",
        "wednesday": "Ср",
        "thursday": "Чт",
        "friday": "Пт",
        "saturday": "Сб",
        "sunday": "Вс",
    }
    
    keyboard_rows = []
    
    # Создаём кнопки для каждого дня
    row = []
    for day_key, day_short in days_map.items():
        checkmark = "✅ " if day_key in selected_days else ""
        row.append(InlineKeyboardButton(
            text=f"{checkmark}{day_short}",
            callback_data=f"day_toggle:{day_key}"
        ))
        if len(row) == 4:  # По 4 кнопки в ряд
            keyboard_rows.append(row)
            row = []
    
    if row:  # Добавляем оставшиеся
        keyboard_rows.append(row)
    
    # Кнопка "Готово"
    keyboard_rows.append([
        InlineKeyboardButton(text="✅ Готово", callback_data="days_confirm")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    return keyboard
