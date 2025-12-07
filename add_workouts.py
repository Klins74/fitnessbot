"""
Добавить тренировки для Вт, Чт, Сб (дни 1, 3, 5)
"""
import asyncio
from db.session import async_session_maker, init_db
from services.workouts import create_workout_template

# Тренировки для недостающих дней (Вт=1, Чт=3, Сб=5)

ADDITIONAL_WORKOUTS = [
    # ===== HOME BEGINNER =====
    # Lose Weight
    {"code": "home_beginner_lose_weight_1", "title": "Кардио табата", "day_index": 1, "level": "beginner", "workout_type": "home", "goal": "lose_weight",
     "exercises": [{"name": "Табата раунд", "sets": 4, "reps": "20сек жұмыс/10сек дем"}, {"name": "Джампинг джек", "sets": 3, "reps": "30"}, {"name": "Скалолаз", "sets": 3, "reps": "20"}, {"name": "Созылу", "sets": 1, "reps": "5 мин"}]},
    {"code": "home_beginner_lose_weight_3", "title": "Күш + тонус", "day_index": 3, "level": "beginner", "workout_type": "home", "goal": "lose_weight",
     "exercises": [{"name": "Отжимания", "sets": 3, "reps": "10"}, {"name": "Приседания", "sets": 3, "reps": "15"}, {"name": "Планка", "sets": 3, "reps": "30 сек"}, {"name": "Выпады", "sets": 3, "reps": "10"}]},
    {"code": "home_beginner_lose_weight_5", "title": "Актив демалыс", "day_index": 5, "level": "beginner", "workout_type": "home", "goal": "lose_weight",
     "exercises": [{"name": "Жаяу серуен", "sets": 1, "reps": "20 мин"}, {"name": "Созылу", "sets": 1, "reps": "15 мин"}, {"name": "Тыныс алу", "sets": 1, "reps": "5 мин"}]},
    
    # Gain Muscle
    {"code": "home_beginner_gain_muscle_1", "title": "Қор + бел", "day_index": 1, "level": "beginner", "workout_type": "home", "goal": "gain_muscle",
     "exercises": [{"name": "Планка", "sets": 4, "reps": "45 сек"}, {"name": "Велосипед", "sets": 4, "reps": "20"}, {"name": "Супермен", "sets": 3, "reps": "15"}, {"name": "Бүйір планка", "sets": 3, "reps": "30 сек"}]},
    {"code": "home_beginner_gain_muscle_3", "title": "Иық + қол", "day_index": 3, "level": "beginner", "workout_type": "home", "goal": "gain_muscle",
     "exercises": [{"name": "Пайк отжимания", "sets": 3, "reps": "10"}, {"name": "Дип орындыққа", "sets": 4, "reps": "12"}, {"name": "Алмас отжимания", "sets": 3, "reps": "10"}, {"name": "Планка", "sets": 3, "reps": "45 сек"}]},
    {"code": "home_beginner_gain_muscle_5", "title": "Қалпына келу", "day_index": 5, "level": "beginner", "workout_type": "home", "goal": "gain_muscle",
     "exercises": [{"name": "Жеңіл созылу", "sets": 1, "reps": "15 мин"}, {"name": "Foam roller", "sets": 1, "reps": "10 мин"}, {"name": "Йога", "sets": 1, "reps": "15 мин"}]},
    
    # Stay Fit
    {"code": "home_beginner_stay_fit_1", "title": "Толық дене", "day_index": 1, "level": "beginner", "workout_type": "home", "goal": "stay_fit",
     "exercises": [{"name": "Отжимания", "sets": 2, "reps": "10"}, {"name": "Приседания", "sets": 2, "reps": "12"}, {"name": "Планка", "sets": 2, "reps": "30 сек"}, {"name": "Выпады", "sets": 2, "reps": "8"}]},
    {"code": "home_beginner_stay_fit_3", "title": "Кардио микс", "day_index": 3, "level": "beginner", "workout_type": "home", "goal": "stay_fit",
     "exercises": [{"name": "Жаяу жүру", "sets": 1, "reps": "15 мин"}, {"name": "Джампинг джек", "sets": 2, "reps": "20"}, {"name": "Созылу", "sets": 1, "reps": "10 мин"}]},
    {"code": "home_beginner_stay_fit_5", "title": "Йога күн", "day_index": 5, "level": "beginner", "workout_type": "home", "goal": "stay_fit",
     "exercises": [{"name": "Йога позалары", "sets": 1, "reps": "20 мин"}, {"name": "Медитация", "sets": 1, "reps": "10 мин"}]},

    # ===== GYM BEGINNER =====
    {"code": "gym_beginner_lose_weight_1", "title": "Кардио марафон", "day_index": 1, "level": "beginner", "workout_type": "gym", "goal": "lose_weight",
     "exercises": [{"name": "Жүгіру доріжка", "sets": 1, "reps": "15 мин"}, {"name": "Эллипс", "sets": 1, "reps": "15 мин"}, {"name": "Велотренажер", "sets": 1, "reps": "10 мин"}]},
    {"code": "gym_beginner_lose_weight_3", "title": "Круговая", "day_index": 3, "level": "beginner", "workout_type": "gym", "goal": "lose_weight",
     "exercises": [{"name": "Кроссовер", "sets": 3, "reps": "12"}, {"name": "Приседания", "sets": 3, "reps": "15"}, {"name": "Тягалау", "sets": 3, "reps": "12"}, {"name": "Кардио", "sets": 1, "reps": "10 мин"}]},
    {"code": "gym_beginner_lose_weight_5", "title": "Бассейн күні", "day_index": 5, "level": "beginner", "workout_type": "gym", "goal": "lose_weight",
     "exercises": [{"name": "Жүзу", "sets": 1, "reps": "30 мин"}, {"name": "Созылу", "sets": 1, "reps": "10 мин"}]},
    
    {"code": "gym_beginner_gain_muscle_1", "title": "Қор күні", "day_index": 1, "level": "beginner", "workout_type": "gym", "goal": "gain_muscle",
     "exercises": [{"name": "Кранч", "sets": 4, "reps": "15"}, {"name": "Планка", "sets": 3, "reps": "45 сек"}, {"name": "Гиперэкстензия", "sets": 3, "reps": "12"}, {"name": "Бүйір бүгу", "sets": 3, "reps": "15"}]},
    {"code": "gym_beginner_gain_muscle_3", "title": "Қайталау күні", "day_index": 3, "level": "beginner", "workout_type": "gym", "goal": "gain_muscle",
     "exercises": [{"name": "Жатып итеру", "sets": 3, "reps": "10"}, {"name": "Тягалау", "sets": 3, "reps": "10"}, {"name": "Иық пресс", "sets": 3, "reps": "10"}, {"name": "Бицепс/Трицепс", "sets": 3, "reps": "10"}]},
    {"code": "gym_beginner_gain_muscle_5", "title": "Кардио + созылу", "day_index": 5, "level": "beginner", "workout_type": "gym", "goal": "gain_muscle",
     "exercises": [{"name": "Жеңіл кардио", "sets": 1, "reps": "20 мин"}, {"name": "Созылу", "sets": 1, "reps": "15 мин"}]},
    
    {"code": "gym_beginner_stay_fit_1", "title": "Функционал", "day_index": 1, "level": "beginner", "workout_type": "gym", "goal": "stay_fit",
     "exercises": [{"name": "TRX жаттығулар", "sets": 3, "reps": "10"}, {"name": "Медбол", "sets": 3, "reps": "12"}, {"name": "Кардио", "sets": 1, "reps": "15 мин"}]},
    {"code": "gym_beginner_stay_fit_3", "title": "Күш + кардио", "day_index": 3, "level": "beginner", "workout_type": "gym", "goal": "stay_fit",
     "exercises": [{"name": "Жатып итеру", "sets": 2, "reps": "10"}, {"name": "Тягалау", "sets": 2, "reps": "10"}, {"name": "Эллипс", "sets": 1, "reps": "15 мин"}]},
    {"code": "gym_beginner_stay_fit_5", "title": "Актив демалыс", "day_index": 5, "level": "beginner", "workout_type": "gym", "goal": "stay_fit",
     "exercises": [{"name": "Сауна", "sets": 1, "reps": "15 мин"}, {"name": "Бассейн", "sets": 1, "reps": "20 мин"}, {"name": "Созылу", "sets": 1, "reps": "10 мин"}]},

    # ===== INTERMEDIATE HOME =====
    {"code": "home_intermediate_lose_weight_1", "title": "Табата интенсив", "day_index": 1, "level": "intermediate", "workout_type": "home", "goal": "lose_weight",
     "exercises": [{"name": "Табата раунд 1", "sets": 8, "reps": "20/10"}, {"name": "Демалыс", "sets": 1, "reps": "1 мин"}, {"name": "Табата раунд 2", "sets": 8, "reps": "20/10"}]},
    {"code": "home_intermediate_lose_weight_3", "title": "EMOM", "day_index": 3, "level": "intermediate", "workout_type": "home", "goal": "lose_weight",
     "exercises": [{"name": "EMOM 20 мин", "sets": 1, "reps": "10 берпи/мин"}]},
    {"code": "home_intermediate_lose_weight_5", "title": "Демалыс кардио", "day_index": 5, "level": "intermediate", "workout_type": "home", "goal": "lose_weight",
     "exercises": [{"name": "Жаяу жүру", "sets": 1, "reps": "30 мин"}, {"name": "Созылу", "sets": 1, "reps": "15 мин"}]},
    
    {"code": "home_intermediate_gain_muscle_1", "title": "Суперсет кеуде", "day_index": 1, "level": "intermediate", "workout_type": "home", "goal": "gain_muscle",
     "exercises": [{"name": "Отжимания + алмас отжимания", "sets": 4, "reps": "10+10"}, {"name": "Пайк + обычный", "sets": 4, "reps": "8+8"}, {"name": "Планка", "sets": 3, "reps": "1 мин"}]},
    {"code": "home_intermediate_gain_muscle_3", "title": "Суперсет аяқ", "day_index": 3, "level": "intermediate", "workout_type": "home", "goal": "gain_muscle",
     "exercises": [{"name": "Приседания + выпады", "sets": 4, "reps": "15+10"}, {"name": "Көпір + икра", "sets": 4, "reps": "15+20"}, {"name": "Планка", "sets": 3, "reps": "1 мин"}]},
    {"code": "home_intermediate_gain_muscle_5", "title": "Қалпына келу", "day_index": 5, "level": "intermediate", "workout_type": "home", "goal": "gain_muscle",
     "exercises": [{"name": "Foam roller", "sets": 1, "reps": "15 мин"}, {"name": "Созылу", "sets": 1, "reps": "15 мин"}, {"name": "Тыныс алу", "sets": 1, "reps": "5 мин"}]},
    
    {"code": "home_intermediate_stay_fit_1", "title": "HIIT микс", "day_index": 1, "level": "intermediate", "workout_type": "home", "goal": "stay_fit",
     "exercises": [{"name": "HIIT", "sets": 1, "reps": "25 мин"}, {"name": "Созылу", "sets": 1, "reps": "10 мин"}]},
    {"code": "home_intermediate_stay_fit_3", "title": "Күш дамыту", "day_index": 3, "level": "intermediate", "workout_type": "home", "goal": "stay_fit",
     "exercises": [{"name": "Отжимания", "sets": 3, "reps": "12"}, {"name": "Приседания", "sets": 3, "reps": "15"}, {"name": "Дип", "sets": 3, "reps": "10"}, {"name": "Выпады", "sets": 3, "reps": "10"}]},
    {"code": "home_intermediate_stay_fit_5", "title": "Йога + медитация", "day_index": 5, "level": "intermediate", "workout_type": "home", "goal": "stay_fit",
     "exercises": [{"name": "Йога", "sets": 1, "reps": "30 мин"}, {"name": "Медитация", "sets": 1, "reps": "15 мин"}]},

    # ===== INTERMEDIATE GYM =====
    {"code": "gym_intermediate_lose_weight_1", "title": "Кардио қарқыны", "day_index": 1, "level": "intermediate", "workout_type": "gym", "goal": "lose_weight",
     "exercises": [{"name": "Интервал жүгіру", "sets": 10, "reps": "1 мин жылдам/1 мин баяу"}, {"name": "Эллипс", "sets": 1, "reps": "15 мин"}]},
    {"code": "gym_intermediate_lose_weight_3", "title": "Күш кешен", "day_index": 3, "level": "intermediate", "workout_type": "gym", "goal": "lose_weight",
     "exercises": [{"name": "Жатып итеру", "sets": 4, "reps": "12"}, {"name": "Тягалау", "sets": 4, "reps": "12"}, {"name": "Приседания", "sets": 4, "reps": "15"}, {"name": "Кардио", "sets": 1, "reps": "15 мин"}]},
    {"code": "gym_intermediate_lose_weight_5", "title": "Бассейн + сауна", "day_index": 5, "level": "intermediate", "workout_type": "gym", "goal": "lose_weight",
     "exercises": [{"name": "Жүзу", "sets": 1, "reps": "45 мин"}, {"name": "Сауна", "sets": 1, "reps": "15 мин"}]},
    
    {"code": "gym_intermediate_gain_muscle_1", "title": "Бицепс + Арқа", "day_index": 1, "level": "intermediate", "workout_type": "gym", "goal": "gain_muscle",
     "exercises": [{"name": "Тягалау блокқа", "sets": 4, "reps": "10"}, {"name": "Қатарлы тартылу", "sets": 4, "reps": "10"}, {"name": "Бицепс штанга", "sets": 4, "reps": "10"}, {"name": "Бицепс гантельмен", "sets": 3, "reps": "12"}]},
    {"code": "gym_intermediate_gain_muscle_3", "title": "Трицепс + Кеуде", "day_index": 3, "level": "intermediate", "workout_type": "gym", "goal": "gain_muscle",
     "exercises": [{"name": "Жатып итеру көлбеу", "sets": 4, "reps": "10"}, {"name": "Кроссовер", "sets": 4, "reps": "12"}, {"name": "Трицепс блок", "sets": 4, "reps": "12"}, {"name": "Дип", "sets": 3, "reps": "макс"}]},
    {"code": "gym_intermediate_gain_muscle_5", "title": "Қор + кардио", "day_index": 5, "level": "intermediate", "workout_type": "gym", "goal": "gain_muscle",
     "exercises": [{"name": "Кранч", "sets": 4, "reps": "20"}, {"name": "Планка", "sets": 3, "reps": "1 мин"}, {"name": "Жеңіл кардио", "sets": 1, "reps": "20 мин"}]},
    
    {"code": "gym_intermediate_stay_fit_1", "title": "Кешенді", "day_index": 1, "level": "intermediate", "workout_type": "gym", "goal": "stay_fit",
     "exercises": [{"name": "Күш жаттығулар", "sets": 3, "reps": "10"}, {"name": "Кардио", "sets": 1, "reps": "20 мин"}, {"name": "Созылу", "sets": 1, "reps": "10 мин"}]},
    {"code": "gym_intermediate_stay_fit_3", "title": "TRX + функционал", "day_index": 3, "level": "intermediate", "workout_type": "gym", "goal": "stay_fit",
     "exercises": [{"name": "TRX кешен", "sets": 1, "reps": "20 мин"}, {"name": "Медбол жаттығулар", "sets": 3, "reps": "10"}, {"name": "Кардио", "sets": 1, "reps": "15 мин"}]},
    {"code": "gym_intermediate_stay_fit_5", "title": "Спа күні", "day_index": 5, "level": "intermediate", "workout_type": "gym", "goal": "stay_fit",
     "exercises": [{"name": "Бассейн", "sets": 1, "reps": "30 мин"}, {"name": "Сауна", "sets": 1, "reps": "15 мин"}, {"name": "Созылу", "sets": 1, "reps": "10 мин"}]},
]


async def add_missing_workouts():
    """Добавить недостающие тренировки"""
    print("Инициализация базы данных...")
    await init_db()
    
    loaded = 0
    skipped = 0
    
    async with async_session_maker() as session:
        for w in ADDITIONAL_WORKOUTS:
            try:
                await create_workout_template(
                    session,
                    code=w["code"],
                    title=w["title"],
                    level=w["level"],
                    workout_type=w["workout_type"],
                    goal=w["goal"],
                    day_index=w["day_index"],
                    exercises=w["exercises"]
                )
                print(f"✅ {w['code']}")
                loaded += 1
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    skipped += 1
                else:
                    print(f"❌ {w['code']}: {e}")
    
    print(f"\n✅ Загружено: {loaded}")
    print(f"⏭ Пропущено: {skipped}")


if __name__ == "__main__":
    asyncio.run(add_missing_workouts())
