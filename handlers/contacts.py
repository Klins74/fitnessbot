"""
Обработчик раздела контактов
"""
from aiogram import Router, F
from aiogram.types import Message

from config import config
from texts_kk import CONTACTS, MENU
from keyboards import get_main_menu_keyboard

router = Router()


@router.message(F.text == MENU["contacts"])
async def show_contacts(message: Message):
    """Отправить информацию о контактах и местоположении"""
    
    # 1. Отправляем текстовое сообщение с информацией
    await message.answer(
        CONTACTS["info_message"],
        parse_mode="Markdown"
    )
    
    # 2. Отправляем venue (местоположение с названием и адресом)
    await message.answer_venue(
        latitude=config.CENTER_LATITUDE,
        longitude=config.CENTER_LONGITUDE,
        title=CONTACTS["venue_title"],
        address=CONTACTS["venue_address"]
    )
    
    # 3. Отправляем контакт с телефоном
    await message.answer_contact(
        phone_number=config.CENTER_PHONE,
        first_name=config.CENTER_NAME
    )
    
    # 4. Завершающее сообщение
    await message.answer(
        "Бізге келуіңізді күтеміз! 👋",
        reply_markup=get_main_menu_keyboard()
    )
