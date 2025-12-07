"""
Состояния FSM для онбординга
"""
from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """Состояния процесса онбординга"""
    gender = State()
    age = State()
    height = State()
    weight = State()
    goal = State()
    level = State()
    workout_type = State()
    confirm = State()
