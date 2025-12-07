"""
Валидаторы данных пользователя
"""
from config import config
from texts_kk import VALIDATION


def validate_age(text: str) -> tuple[bool, int | None, str]:
    """
    Валидация возраста
    Returns: (is_valid, value, error_message)
    """
    try:
        age = int(text)
        if config.MIN_AGE <= age <= config.MAX_AGE:
            return True, age, ""
        return False, None, VALIDATION["invalid_age"]
    except ValueError:
        return False, None, VALIDATION["invalid_number"]


def validate_height(text: str) -> tuple[bool, int | None, str]:
    """
    Валидация роста
    Returns: (is_valid, value, error_message)
    """
    try:
        height = int(text)
        if config.MIN_HEIGHT <= height <= config.MAX_HEIGHT:
            return True, height, ""
        return False, None, VALIDATION["invalid_height"]
    except ValueError:
        return False, None, VALIDATION["invalid_number"]


def validate_weight(text: str) -> tuple[bool, float | None, str]:
    """
    Валидация веса
    Returns: (is_valid, value, error_message)
    """
    try:
        weight = float(text.replace(",", "."))
        if config.MIN_WEIGHT <= weight <= config.MAX_WEIGHT:
            return True, weight, ""
        return False, None, VALIDATION["invalid_weight"]
    except ValueError:
        return False, None, VALIDATION["invalid_number"]


def validate_time(text: str) -> tuple[bool, str | None, str]:
    """
    Валидация времени в формате HH:MM
    Returns: (is_valid, value, error_message)
    """
    try:
        parts = text.split(":")
        if len(parts) != 2:
            return False, None, "Формат: HH:MM (мысалы: 18:00)"
        
        hour, minute = int(parts[0]), int(parts[1])
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return True, f"{hour:02d}:{minute:02d}", ""
        return False, None, "Сағат 0-23, минут 0-59 аралығында болуы керек"
    except ValueError:
        return False, None, "Формат: HH:MM (мысалы: 18:00)"
