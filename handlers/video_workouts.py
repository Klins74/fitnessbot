"""
Обработчик раздела видео-тренировок
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from texts_kk import MENU, VIDEO_WORKOUTS
from keyboards import get_video_categories_keyboard, get_video_list_keyboard, get_main_menu_keyboard

router = Router()

# База данных видео (позже можно перенести в БД)
VIDEOS_DB = {
    "strength": [
        {
            "title": "Күш жаттығуы - Толық денені жаттықтыру",
            "duration": "30 минут",
            "description": "Толық дене үшін күш жаттығуы. Штангасыз, тек өз салмағыңызбен.",
            "url": "https://youtu.be/2pLT-olgUJs?si=2XBpJaOB3XpVIioH"
        },
        {
            "title": "Үйде күш жаттығуы - Бастауышқа",
            "duration": "20 минут",
            "description": "Үй үшін қарапайым күш жаттығулары. Жабдықсыз.",
            "url": "https://www.youtube.com/watch?v=ml6cT4AZdqI"
        },
        {
            "title": "Бұлшық ет жинау - Толық жаттығу",
            "duration": "35 минут",
            "description": "Бұлшық ет массасын арттыру үшін интенсивті жаттығу.",
            "url": "https://www.youtube.com/watch?v=oAPCPjnU1wA"
        },
    ],
    "cardio": [
        {
            "title": "Кардио жаттығу - Майды жағу",
            "duration": "25 минут",
            "description": "Интенсивті кардио жаттығу майды жағу үшін.",
            "url": "https://youtu.be/6TmQiugy_qw?si=xuP9025U0Olc7FDj"
        },
        {
            "title": "HIIT жаттығуы - Жылдам нәтиже",
            "duration": "15 минут",
            "description": "Жоғары интенсивті интервалды жаттығу. Тез майды жағу.",
            "url": "https://www.youtube.com/watch?v=M0uO8X3_tEA"
        },
        {
            "title": "Кардио үйде - Секіріссіз",
            "duration": "30 минут",
            "description": "Үй үшін кардио жаттығу. Көршілерге кедергі жоқ.",
            "url": "https://www.youtube.com/watch?v=gC_L9qAHVJ8"
        },
        {
            "title": "Жүгіру жаттығуы - Бастауышқа",
            "duration": "20 минут",
            "description": "Жүгіруге үйрету бағдарламасы бастаушыларға.",
            "url": "https://www.youtube.com/watch?v=brFHyOtTwH4"
        },
    ],
    "stretching": [
        {
            "title": "Созылу жаттығуы - Икемділік",
            "duration": "15 минут",
            "description": "Бұлшық еттерді босаңсыту және икемділікті арттыру.",
            "url": "https://youtu.be/miPJFOj-9m0?si=Kzc40HuW8GI06wk5"
        },
        {
            "title": "Йога бастауышқа - Таңғы жаттығу",
            "duration": "20 минут",
            "description": "Таңертең үшін жеңіл йога. Энергия мен серпілділік.",
            "url": "https://www.youtube.com/watch?v=v7AYKMP6rOE"
        },
        {
            "title": "Арқа үшін созылу - Ауырсынуды жою",
            "duration": "12 минут",
            "description": "Арқа ауырсынуын азайту үшін созылу жаттығулары.",
            "url": "https://www.youtube.com/watch?v=4pKly2JojMw"
        },
    ],
}


@router.message(F.text == MENU["video_workouts"])
async def show_video_categories(message: Message):
    """Показать категории видео"""
    await message.answer(
        VIDEO_WORKOUTS["title"],
        reply_markup=get_video_categories_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "video_categories")
async def back_to_categories(callback: CallbackQuery):
    """Вернуться к категориям"""
    await callback.message.edit_text(
        VIDEO_WORKOUTS["title"],
        reply_markup=get_video_categories_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("video_cat:"))
async def show_category_videos(callback: CallbackQuery):
    """Показать видео из категории"""
    category = callback.data.split(":")[1]
    
    videos = VIDEOS_DB.get(category, [])
    
    if not videos:
        await callback.answer(VIDEO_WORKOUTS["no_videos"], show_alert=True)
        return
    
    # Отправляем каждое видео отдельным сообщением
    for video in videos:
        text = VIDEO_WORKOUTS["video_format"].format(
            title=video["title"],
            duration=video["duration"],
            description=video["description"],
            url=video["url"]
        )
        await callback.message.answer(text, parse_mode="Markdown")
    
    # Кнопка "Назад к категориям"
    await callback.message.answer(
        "Басқа категорияны таңдау үшін төмендегі батырманы басыңыз:",
        reply_markup=get_video_list_keyboard(category)
    )
    
    await callback.answer()
