"""
Сервис для работы с AI (Groq - быстрый и бесплатный)
"""
import aiohttp
import json
import logging
from config import config

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # Мощная модель с лучшей поддержкой казахского


async def _call_groq(messages: list, max_tokens: int = 1000) -> str:
    """Вызов Groq API"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": GROQ_MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.8  # Больше креативности
            }
            
            async with session.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    error = await response.text()
                    logger.error(f"Groq API Error: {response.status} - {error}")
                    return ""
    except Exception as e:
        logger.error(f"Groq Exception: {e}")
        return ""


async def get_ai_advice(
    user_profile: dict,
    workout_title: str,
    feeling: str
) -> str:
    """Получить AI-совет после тренировки"""
    messages = [
        {
            "role": "system",
            "content": (
                "Сіз қазақ тілінде сөйлейтін кәсіби фитнес жаттықтырушысыз. "
                "Толық, толыққанды және мотивациялық жауап беріңіз. "
                "Кемінде 5-7 сөйлем жазыңыз. Егер адам жақсы сезінсе - құттықтап, "
                "ары қарай кеңес беріңіз. Егер қиын болса - қолдау көрсетіп, "
                "жеңілдету жолдарын ұсыныңыз."
            )
        },
        {
            "role": "user",
            "content": f"Жаттығу аты: {workout_title}\nМенің сезімім: {feeling}\n\nМаған толық кеңес пен мотивация беріңіз."
        }
    ]
    
    response = await _call_groq(messages, max_tokens=800)
    return response if response else "Тамаша жұмыс! Жалғастыра беріңіз! 💪🔥"


async def get_nutrition_advice(user_profile: dict) -> str:
    """Получить AI-совет по питанию"""
    goal = user_profile.get('goal', 'белгісіз')
    weight = user_profile.get('weight_kg', '')
    height = user_profile.get('height_cm', '')
    
    messages = [
        {
            "role": "system",
            "content": (
                "Сіз қазақ тілінде сөйлейтін кәсіби тамақтану жаттықтырушысыз. "
                "Толық, егжей-тегжейлі және практикалық кеңес беріңіз. "
                "Кемінде 8-10 сөйлем жазыңыз. Нақты тағамдар мен рецепттерді атаңыз. "
                "Күнделікті тамақтану кестесін ұсыныңыз."
            )
        },
        {
            "role": "user",
            "content": (
                f"Менің мақсатым: {goal}\n"
                f"Салмағым: {weight} кг\n"
                f"Бойым: {height} см\n\n"
                f"Маған толық тамақтану жоспары мен кеңес беріңіз. "
                f"Не жеу керек, қалай дайындау керек және қанша жеу керек екенін айтыңыз."
            )
        }
    ]
    
    response = await _call_groq(messages, max_tokens=1200)
    return response if response else "Қазір кеңес алу мүмкін емес."


async def ask_ai_trainer(question: str, user_profile: dict) -> str:
    """Задать вопрос AI-тренеру"""
    goal = user_profile.get('goal', '')
    level = user_profile.get('level', '')
    
    messages = [
        {
            "role": "system", 
            "content": (
                "Сіз қазақ тілінде сөйлейтін кәсіби фитнес жаттықтырушысыз. "
                "Толық, егжей-тегжейлі және пайдалы жауап беріңіз. "
                "Кемінде 6-8 сөйлем жазыңыз. Нақты мысалдар мен кеңестер беріңіз. "
                "Егер сұрақ жаттығу техникасы туралы болса - қадамдық нұсқаулық беріңіз."
            )
        },
        {
            "role": "user",
            "content": (
                f"Менің профилім: мақсат - {goal}, деңгей - {level}\n\n"
                f"Сұрақ: {question}\n\n"
                f"Толық және түсінікті жауап беріңіз."
            )
        }
    ]
    
    response = await _call_groq(messages, max_tokens=1000)
    return response if response else "Қазір жауап алу мүмкін емес."
