"""
Скрипт для загрузки базовых тренировок в БД
Покрывает все комбинации: goal + level + workout_type + days
"""
import asyncio
from db.session import async_session_maker, init_db
from services.workouts import create_workout_template

# ===== ДОМАШНИЕ ТРЕНИРОВКИ =====

# Beginner + Home + Lose Weight (Пн, Ср, Пт, Вс)
HOME_BEGINNER_LOSE_WEIGHT = [
    {
        "code": "home_beginner_lose_weight_0",
        "title": "Кардио + Күш жаттығулары",
        "day_index": 0,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "5 мин"},
            {"name": "Джампинг домкрат", "sets": 3, "reps": "30 сек"},
            {"name": "Отжимания", "sets": 3, "reps": "10"},
            {"name": "Приседания", "sets": 3, "reps": "15"},
            {"name": "Планка", "sets": 3, "reps": "30 сек"},
        ]
    },
    {
        "code": "home_beginner_lose_weight_2",
        "title": "Аяқ + Кардио",
        "day_index": 2,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "5 мин"},
            {"name": "Приседания", "sets": 4, "reps": "15"},
            {"name": "Выпады", "sets": 3, "reps": "10 әр аяққа"},
            {"name": "Көпір", "sets": 3, "reps": "15"},
            {"name": "Бег на орнында", "sets": 3, "reps": "1 мин"},
        ]
    },
    {
        "code": "home_beginner_lose_weight_4",
        "title": "Интенсивті кардио",
        "day_index": 4,
        "exercises": [
            {"name": "Берпи", "sets": 3, "reps": "8"},
            {"name": "Жоғары тізелер", "sets": 3, "reps": "30 сек"},
            {"name": "Скалолаз", "sets": 3, "reps": "20"},
            {"name": "Скакалка", "sets": 3, "reps": "1 мин"},
            {"name": "Созылу", "sets": 1, "reps": "5 мин"},
        ]
    },
    {
        "code": "home_beginner_lose_weight_6",
        "title": "Жеңіл кардио + Созылу",
        "day_index": 6,
        "exercises": [
            {"name": "Жаяу жүру", "sets": 1, "reps": "15 мин"},
            {"name": "Йога позалары", "sets": 1, "reps": "10 мин"},
            {"name": "Созылу жаттығулары", "sets": 1, "reps": "10 мин"},
        ]
    },
]

# Beginner + Home + Gain Muscle
HOME_BEGINNER_GAIN_MUSCLE = [
    {
        "code": "home_beginner_gain_muscle_0",
        "title": "Кеуде + Қол",
        "day_index": 0,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "5 мин"},
            {"name": "Отжимания", "sets": 4, "reps": "12"},
            {"name": "Алмас отжимания", "sets": 3, "reps": "10"},
            {"name": "Дип (орындыққа)", "sets": 3, "reps": "12"},
            {"name": "Планка", "sets": 3, "reps": "45 сек"},
        ]
    },
    {
        "code": "home_beginner_gain_muscle_2",
        "title": "Арқа + Иық",
        "day_index": 2,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "5 мин"},
            {"name": "Супермен", "sets": 4, "reps": "15"},
            {"name": "Кері жатып тартылу", "sets": 3, "reps": "10"},
            {"name": "Иыққа жаттығу", "sets": 3, "reps": "15"},
            {"name": "Планка бүйір", "sets": 3, "reps": "30 сек"},
        ]
    },
    {
        "code": "home_beginner_gain_muscle_4",
        "title": "Аяқтар",
        "day_index": 4,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "5 мин"},
            {"name": "Приседания", "sets": 4, "reps": "15"},
            {"name": "Выпады", "sets": 3, "reps": "12 әр аяққа"},
            {"name": "Көпір", "sets": 4, "reps": "15"},
            {"name": "Икрге көтерілу", "sets": 4, "reps": "20"},
        ]
    },
    {
        "code": "home_beginner_gain_muscle_6",
        "title": "Толық дене",
        "day_index": 6,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "5 мин"},
            {"name": "Берпи", "sets": 3, "reps": "10"},
            {"name": "Отжимания", "sets": 3, "reps": "10"},
            {"name": "Приседания", "sets": 3, "reps": "15"},
            {"name": "Созылу", "sets": 1, "reps": "5 мин"},
        ]
    },
]

# Beginner + Home + Stay Fit
HOME_BEGINNER_STAY_FIT = [
    {
        "code": "home_beginner_stay_fit_0",
        "title": "Жалпы форма",
        "day_index": 0,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "5 мин"},
            {"name": "Отжимания", "sets": 3, "reps": "10"},
            {"name": "Приседания", "sets": 3, "reps": "15"},
            {"name": "Планка", "sets": 3, "reps": "30 сек"},
            {"name": "Созылу", "sets": 1, "reps": "5 мин"},
        ]
    },
    {
        "code": "home_beginner_stay_fit_2",
        "title": "Кардио + Баланс",
        "day_index": 2,
        "exercises": [
            {"name": "Жаяу жүру", "sets": 1, "reps": "10 мин"},
            {"name": "Bir аяқта тұру", "sets": 3, "reps": "30 сек"},
            {"name": "Жеңіл кардио", "sets": 3, "reps": "2 мин"},
            {"name": "Йога", "sets": 1, "reps": "10 мин"},
        ]
    },
    {
        "code": "home_beginner_stay_fit_4",
        "title": "Созылу + Күш",
        "day_index": 4,
        "exercises": [
            {"name": "Динамикалық созылу", "sets": 1, "reps": "5 мин"},
            {"name": "Отжимания", "sets": 2, "reps": "10"},
            {"name": "Приседания", "sets": 2, "reps": "12"},
            {"name": "Йога", "sets": 1, "reps": "15 мин"},
        ]
    },
    {
        "code": "home_beginner_stay_fit_6",
        "title": "Актив демалыс",
        "day_index": 6,
        "exercises": [
            {"name": "Жаяу серуен", "sets": 1, "reps": "20 мин"},
            {"name": "Жеңіл созылу", "sets": 1, "reps": "10 мин"},
            {"name": "Тыныс алу жаттығулары", "sets": 1, "reps": "5 мин"},
        ]
    },
]

# ===== ЗАЛДА ТРЕНИРОВКИ =====

# Beginner + Gym + Lose Weight
GYM_BEGINNER_LOSE_WEIGHT = [
    {
        "code": "gym_beginner_lose_weight_0",
        "title": "Кардио + Күш",
        "day_index": 0,
        "exercises": [
            {"name": "Жүгіру доріжка", "sets": 1, "reps": "10 мин"},
            {"name": "Жатып итеру", "sets": 3, "reps": "12"},
            {"name": "Тягалау блокқа", "sets": 3, "reps": "12"},
            {"name": "Велотренажер", "sets": 1, "reps": "15 мин"},
        ]
    },
    {
        "code": "gym_beginner_lose_weight_2",
        "title": "Аяқ + Кардио",
        "day_index": 2,
        "exercises": [
            {"name": "Эллипс", "sets": 1, "reps": "10 мин"},
            {"name": "Аяқ пресс", "sets": 4, "reps": "12"},
            {"name": "Выпады гантельмен", "sets": 3, "reps": "10"},
            {"name": "Жүгіру", "sets": 1, "reps": "15 мин"},
        ]
    },
    {
        "code": "gym_beginner_lose_weight_4",
        "title": "HIIT тренировка",
        "day_index": 4,
        "exercises": [
            {"name": "Жүгіру (интервал)", "sets": 10, "reps": "30 сек жүгіру / 30 сек жүру"},
            {"name": "Берпи", "sets": 3, "reps": "10"},
            {"name": "Скалолаз", "sets": 3, "reps": "20"},
            {"name": "Велотренажер", "sets": 1, "reps": "10 мин"},
        ]
    },
    {
        "code": "gym_beginner_lose_weight_6",
        "title": "Жеңіл кардио",
        "day_index": 6,
        "exercises": [
            {"name": "Эллипс", "sets": 1, "reps": "30 мин"},
            {"name": "Созылу", "sets": 1, "reps": "10 мин"},
        ]
    },
]

# Beginner + Gym + Gain Muscle
GYM_BEGINNER_GAIN_MUSCLE = [
    {
        "code": "gym_beginner_gain_muscle_0",
        "title": "Кеуде + Трицепс",
        "day_index": 0,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "10 мин"},
            {"name": "Жатып итеру штанга", "sets": 4, "reps": "8-10"},
            {"name": "Көлбеу жатып итеру", "sets": 3, "reps": "10"},
            {"name": "Кроссовер", "sets": 3, "reps": "12"},
            {"name": "Трицепс блок", "sets": 3, "reps": "12"},
        ]
    },
    {
        "code": "gym_beginner_gain_muscle_2",
        "title": "Арқа + Бицепс",
        "day_index": 2,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "10 мин"},
            {"name": "Тягалау блокқа", "sets": 4, "reps": "10"},
            {"name": "Қатарлы тартылу", "sets": 3, "reps": "10"},
            {"name": "Гиперэкстензия", "sets": 3, "reps": "12"},
            {"name": "Бицепс штанга", "sets": 3, "reps": "10"},
        ]
    },
    {
        "code": "gym_beginner_gain_muscle_4",
        "title": "Аяқтар + Иық",
        "day_index": 4,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "10 мин"},
            {"name": "Приседания штанга", "sets": 4, "reps": "8-10"},
            {"name": "Аяқ пресс", "sets": 3, "reps": "12"},
            {"name": "Иық жатып итеру", "sets": 4, "reps": "10"},
            {"name": "Бүйірге көтеру", "sets": 3, "reps": "12"},
        ]
    },
    {
        "code": "gym_beginner_gain_muscle_6",
        "title": "Толық дене",
        "day_index": 6,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "10 мин"},
            {"name": "Жатып итеру", "sets": 3, "reps": "10"},
            {"name": "Тягалау", "sets": 3, "reps": "10"},
            {"name": "Приседания", "sets": 3, "reps": "12"},
            {"name": "Планка", "sets": 3, "reps": "45 сек"},
        ]
    },
]

# Beginner + Gym + Stay Fit
GYM_BEGINNER_STAY_FIT = [
    {
        "code": "gym_beginner_stay_fit_0",
        "title": "Жалпы форма",
        "day_index": 0,
        "exercises": [
            {"name": "Кардио", "sets": 1, "reps": "15 мин"},
            {"name": "Жатып итеру", "sets": 3, "reps": "10"},
            {"name": "Тягалау", "sets": 3, "reps": "10"},
            {"name": "Приседания", "sets": 3, "reps": "12"},
            {"name": "Созылу", "sets": 1, "reps": "5 мин"},
        ]
    },
    {
        "code": "gym_beginner_stay_fit_2",
        "title": "Кардио күн",
        "day_index": 2,
        "exercises": [
            {"name": "Эллипс", "sets": 1, "reps": "20 мин"},
            {"name": "Велотренажер", "sets": 1, "reps": "15 мин"},
            {"name": "Созылу", "sets": 1, "reps": "10 мин"},
        ]
    },
    {
        "code": "gym_beginner_stay_fit_4",
        "title": "Күш + Баланс",
        "day_index": 4,
        "exercises": [
            {"name": "Жылу жаттығуы", "sets": 1, "reps": "10 мин"},
            {"name": "Жеңіл күш жаттығулары", "sets": 3, "reps": "12"},
            {"name": "TRX жаттығулары", "sets": 3, "reps": "10"},
            {"name": "Созылу", "sets": 1, "reps": "10 мин"},
        ]
    },
    {
        "code": "gym_beginner_stay_fit_6",
        "title": "Актив демалыс",
        "day_index": 6,
        "exercises": [
            {"name": "Жеңіл жаяу жүру", "sets": 1, "reps": "30 мин"},
            {"name": "Бассейн", "sets": 1, "reps": "20 мин"},
        ]
    },
]

# ===== INTERMEDIATE LEVEL =====

# Intermediate + Home + All Goals
HOME_INTERMEDIATE_LOSE_WEIGHT = [
    {"code": "home_intermediate_lose_weight_0", "title": "HIIT кардио", "day_index": 0, 
     "exercises": [{"name": "Берпи", "sets": 4, "reps": "12"}, {"name": "Жоғары тізелер", "sets": 4, "reps": "45 сек"}, {"name": "Скалолаз", "sets": 4, "reps": "30"}, {"name": "Джампинг сквот", "sets": 4, "reps": "15"}]},
    {"code": "home_intermediate_lose_weight_2", "title": "Табата", "day_index": 2,
     "exercises": [{"name": "Табата раунд 1", "sets": 8, "reps": "20 сек жұмыс / 10 сек дем"}, {"name": "Табата раунд 2", "sets": 8, "reps": "20 сек / 10 сек"}]},
    {"code": "home_intermediate_lose_weight_4", "title": "Күш + кардио", "day_index": 4,
     "exercises": [{"name": "Отжимания", "sets": 4, "reps": "15"}, {"name": "Приседания", "sets": 4, "reps": "20"}, {"name": "Планка", "sets": 4, "reps": "1 мин"}, {"name": "Кардио", "sets": 1, "reps": "15 мин"}]},
    {"code": "home_intermediate_lose_weight_6", "title": "Актив демалыс", "day_index": 6,
     "exercises": [{"name": "Йога", "sets": 1, "reps": "30 мин"}, {"name": "Созылу", "sets": 1, "reps": "15 мин"}]},
]

HOME_INTERMEDIATE_GAIN_MUSCLE = [
    {"code": "home_intermediate_gain_muscle_0", "title": "Жоғарғы дене", "day_index": 0,
     "exercises": [{"name": "Отжимания", "sets": 5, "reps": "15"}, {"name": "Алмас отжимания", "sets": 4, "reps": "12"}, {"name": "Пайк отжимания", "sets": 3, "reps": "10"}, {"name": "Дип", "sets": 4, "reps": "12"}]},
    {"code": "home_intermediate_gain_muscle_2", "title": "Аяқтар", "day_index": 2,
     "exercises": [{"name": "Приседания", "sets": 5, "reps": "20"}, {"name": "Пистоль сквот", "sets": 3, "reps": "5"}, {"name": "Выпады секіру", "sets": 4, "reps": "12"}, {"name": "Көпір", "sets": 4, "reps": "20"}]},
    {"code": "home_intermediate_gain_muscle_4", "title": "Арқа + Қор", "day_index": 4,
     "exercises": [{"name": "Супермен", "sets": 4, "reps": "20"}, {"name": "Кері планка", "sets": 3, "reps": "45 сек"}, {"name": "Планка", "sets": 4, "reps": "1 мин"}, {"name": "Велосипед", "sets": 4, "reps": "20"}]},
    {"code": "home_intermediate_gain_muscle_6", "title": "Толық дене", "day_index": 6,
     "exercises": [{"name": "Берпи", "sets": 4, "reps": "10"}, {"name": "Отжимания", "sets": 3, "reps": "12"}, {"name": "Приседания", "sets": 3, "reps": "15"}, {"name": "Планка", "sets": 3, "reps": "1 мин"}]},
]

HOME_INTERMEDIATE_STAY_FIT = [
    {"code": "home_intermediate_stay_fit_0", "title": "Функционал", "day_index": 0,
     "exercises": [{"name": "Динамикалық созылу", "sets": 1, "reps": "5 мин"}, {"name": "Отжимания", "sets": 3, "reps": "12"}, {"name": "Приседания", "sets": 3, "reps": "15"}, {"name": "Планка", "sets": 3, "reps": "45 сек"}]},
    {"code": "home_intermediate_stay_fit_2", "title": "Кардио", "day_index": 2,
     "exercises": [{"name": "HIIT", "sets": 1, "reps": "20 мин"}, {"name": "Созылу", "sets": 1, "reps": "10 мин"}]},
    {"code": "home_intermediate_stay_fit_4", "title": "Күш + Баланс", "day_index": 4,
     "exercises": [{"name": "Bir аяқта жаттығулар", "sets": 3, "reps": "10"}, {"name": "Йога", "sets": 1, "reps": "20 мин"}]},
    {"code": "home_intermediate_stay_fit_6", "title": "Демалыс", "day_index": 6,
     "exercises": [{"name": "Жеңіл серуен", "sets": 1, "reps": "30 мин"}, {"name": "Медитация", "sets": 1, "reps": "10 мин"}]},
]

# Intermediate + Gym templates
GYM_INTERMEDIATE_LOSE_WEIGHT = [
    {"code": "gym_intermediate_lose_weight_0", "title": "HIIT + Күш", "day_index": 0,
     "exercises": [{"name": "Жүгіру интервал", "sets": 10, "reps": "1 мин жүгіру / 1 мин жүру"}, {"name": "Күш кешені", "sets": 3, "reps": "10"}, {"name": "Кардио", "sets": 1, "reps": "15 мин"}]},
    {"code": "gym_intermediate_lose_weight_2", "title": "Круговая", "day_index": 2,
     "exercises": [{"name": "Круговая тренировка", "sets": 4, "reps": "8 жаттығу х 45 сек"}]},
    {"code": "gym_intermediate_lose_weight_4", "title": "Кардио марафон", "day_index": 4,
     "exercises": [{"name": "Эллипс", "sets": 1, "reps": "20 мин"}, {"name": "Жүгіру", "sets": 1, "reps": "15 мин"}, {"name": "Велотренажер", "sets": 1, "reps": "15 мин"}]},
    {"code": "gym_intermediate_lose_weight_6", "title": "Актив демалыс", "day_index": 6,
     "exercises": [{"name": "Бассейн", "sets": 1, "reps": "45 мин"}]},
]

GYM_INTERMEDIATE_GAIN_MUSCLE = [
    {"code": "gym_intermediate_gain_muscle_0", "title": "Кеуде", "day_index": 0,
     "exercises": [{"name": "Жатып итеру штанга", "sets": 5, "reps": "5"}, {"name": "Көлбеу жатып итеру", "sets": 4, "reps": "8"}, {"name": "Кроссовер", "sets": 4, "reps": "12"}, {"name": "Дип", "sets": 3, "reps": "макс"}]},
    {"code": "gym_intermediate_gain_muscle_2", "title": "Арқа", "day_index": 2,
     "exercises": [{"name": "Становая тяга", "sets": 5, "reps": "5"}, {"name": "Тягалау блокқа", "sets": 4, "reps": "10"}, {"name": "Қатарлы тартылу", "sets": 4, "reps": "10"}, {"name": "Гиперэкстензия", "sets": 3, "reps": "15"}]},
    {"code": "gym_intermediate_gain_muscle_4", "title": "Аяқтар", "day_index": 4,
     "exercises": [{"name": "Приседания", "sets": 5, "reps": "5"}, {"name": "Жатып түсу", "sets": 4, "reps": "10"}, {"name": "Выпады", "sets": 3, "reps": "12"}, {"name": "Икрге көтерілу", "sets": 4, "reps": "15"}]},
    {"code": "gym_intermediate_gain_muscle_6", "title": "Иық + Қол", "day_index": 6,
     "exercises": [{"name": "Армия жатып итеру", "sets": 4, "reps": "8"}, {"name": "Бүйірге көтеру", "sets": 4, "reps": "12"}, {"name": "Бицепс", "sets": 4, "reps": "10"}, {"name": "Трицепс", "sets": 4, "reps": "10"}]},
]

GYM_INTERMEDIATE_STAY_FIT = [
    {"code": "gym_intermediate_stay_fit_0", "title": "Толық дене А", "day_index": 0,
     "exercises": [{"name": "Кардио", "sets": 1, "reps": "15 мин"}, {"name": "Күш жаттығулар", "sets": 3, "reps": "10"}, {"name": "Созылу", "sets": 1, "reps": "10 мин"}]},
    {"code": "gym_intermediate_stay_fit_2", "title": "Кардио", "day_index": 2,
     "exercises": [{"name": "Интервал жүгіру", "sets": 1, "reps": "25 мин"}, {"name": "Эллипс", "sets": 1, "reps": "15 мин"}]},
    {"code": "gym_intermediate_stay_fit_4", "title": "Толық дене Б", "day_index": 4,
     "exercises": [{"name": "Функционал тренировка", "sets": 1, "reps": "30 мин"}, {"name": "Созылу", "sets": 1, "reps": "10 мин"}]},
    {"code": "gym_intermediate_stay_fit_6", "title": "Актив демалыс", "day_index": 6,
     "exercises": [{"name": "Йога", "sets": 1, "reps": "45 мин"}]},
]


def generate_all_templates():
    """Генерация всех шаблонов тренировок"""
    all_templates = []
    
    template_groups = [
        (HOME_BEGINNER_LOSE_WEIGHT, "beginner", "home", "lose_weight"),
        (HOME_BEGINNER_GAIN_MUSCLE, "beginner", "home", "gain_muscle"),
        (HOME_BEGINNER_STAY_FIT, "beginner", "home", "stay_fit"),
        (GYM_BEGINNER_LOSE_WEIGHT, "beginner", "gym", "lose_weight"),
        (GYM_BEGINNER_GAIN_MUSCLE, "beginner", "gym", "gain_muscle"),
        (GYM_BEGINNER_STAY_FIT, "beginner", "gym", "stay_fit"),
        (HOME_INTERMEDIATE_LOSE_WEIGHT, "intermediate", "home", "lose_weight"),
        (HOME_INTERMEDIATE_GAIN_MUSCLE, "intermediate", "home", "gain_muscle"),
        (HOME_INTERMEDIATE_STAY_FIT, "intermediate", "home", "stay_fit"),
        (GYM_INTERMEDIATE_LOSE_WEIGHT, "intermediate", "gym", "lose_weight"),
        (GYM_INTERMEDIATE_GAIN_MUSCLE, "intermediate", "gym", "gain_muscle"),
        (GYM_INTERMEDIATE_STAY_FIT, "intermediate", "gym", "stay_fit"),
    ]
    
    for templates, level, workout_type, goal in template_groups:
        for t in templates:
            all_templates.append({
                "code": t["code"],
                "title": t["title"],
                "level": level,
                "workout_type": workout_type,
                "goal": goal,
                "day_index": t["day_index"],
                "exercises": t["exercises"]
            })
    
    return all_templates


async def load_workouts():
    """Загрузка тренировок в БД"""
    print("Инициализация базы данных...")
    await init_db()
    print("База данных готова\n")
    
    all_templates = generate_all_templates()
    print(f"Подготовлено {len(all_templates)} шаблонов тренировок\n")
    
    loaded = 0
    skipped = 0
    
    async with async_session_maker() as session:
        for template in all_templates:
            try:
                await create_workout_template(
                    session,
                    code=template["code"],
                    title=template["title"],
                    level=template["level"],
                    workout_type=template["workout_type"],
                    goal=template["goal"],
                    day_index=template["day_index"],
                    exercises=template["exercises"]
                )
                print(f"✅ {template['code']}")
                loaded += 1
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    skipped += 1
                else:
                    print(f"❌ {template['code']}: {e}")
    
    print(f"\n✅ Загружено: {loaded}")
    print(f"⏭ Пропущено (уже есть): {skipped}")
    print(f"📊 Всего: {loaded + skipped}")


if __name__ == "__main__":
    asyncio.run(load_workouts())
