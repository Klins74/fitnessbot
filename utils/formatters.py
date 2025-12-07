"""
Форматтеры данных для отображения
"""
from texts_kk import GENDERS, GOALS, LEVELS, WORKOUT_TYPES


def format_gender(gender: str) -> str:
    """Форматирование пола"""
    return GENDERS.get(gender, gender)


def format_goal(goal: str) -> str:
    """Форматирование цели"""
    return GOALS.get(goal, goal)


def format_level(level: str) -> str:
    """Форматирование уровня"""
    return LEVELS.get(level, level)


def format_workout_type(workout_type: str) -> str:
    """Форматирование типа тренировки"""
    return WORKOUT_TYPES.get(workout_type, workout_type)


def format_profile(user_data: dict) -> str:
    """Форматирование профиля пользователя для отображения"""
    from texts_kk import ONBOARDING
    
    return ONBOARDING["confirm_profile"].format(
        gender=format_gender(user_data.get("gender", "")),
        age=user_data.get("age", ""),
        height=user_data.get("height", ""),
        weight=user_data.get("weight", ""),
        goal=format_goal(user_data.get("goal", "")),
        level=format_level(user_data.get("level", "")),
        workout_type=format_workout_type(user_data.get("workout_type", ""))
    )


def format_workout(workout: dict) -> str:
    """Форматирование тренировки для отображения"""
    from texts_kk import WORKOUTS
    
    exercises_text = "\n".join([
        WORKOUTS["exercise_format"].format(
            name=ex["name"],
            sets=ex["sets"],
            reps=ex["reps"]
        )
        for ex in workout.get("exercises", [])
    ])
    
    return WORKOUTS["workout_for_today"].format(title=workout.get("title", "")) + "\n" + exercises_text
