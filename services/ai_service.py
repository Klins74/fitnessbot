"""
Сервис для работы с AI (Groq - быстрый и бесплатный)
"""
import aiohttp
import json
import logging
from config import config

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"  # Быстрая бесплатная модель


async def _call_groq(messages: list) -> str:
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
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            async with session.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
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
            "content": "Сен қазақ тілінде сөйлейтін фитнес жаттықтырушысың. Қысқа жауап бер (2-3 сөйлем)."
        },
        {
            "role": "user",
            "content": f"Жаттығу: {workout_title}. Сезім: {feeling}. Мотивация бер."
        }
    ]
    
    response = await _call_groq(messages)
    return response if response else "Тамаша жұмыс! Жалғастыра беріңіз! 💪🔥"


async def get_nutrition_advice(user_profile: dict) -> str:
    """Получить AI-совет по питанию"""
    goal = user_profile.get('goal', 'белгісіз')
    
    messages = [
        {
            "role": "system",
            "content": "Сен қазақ тілінде сөйлейтін тамақтану жаттықтырушысың."
        },
        {
            "role": "user",
            "content": f"Мақсат: {goal}. Қысқа тамақтану кеңесі бер (4 пункт)."
        }
    ]
    
    response = await _call_groq(messages)
    return response if response else "Қазір кеңес алу мүмкін емес."


async def ask_ai_trainer(question: str, user_profile: dict) -> str:
    """Задать вопрос AI-тренеру"""
    messages = [
        {
            "role": "system", 
            "content": "Сен қазақ тілінде сөйлейтін фитнес жаттықтырушысың. Қысқа жауап бер."
        },
        {
            "role": "user",
            "content": question
        }
    ]
    
    response = await _call_groq(messages)
    return response if response else "Қазір жауап алу мүмкін емес."
