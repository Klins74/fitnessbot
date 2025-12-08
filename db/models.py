"""
Модели базы данных
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # Профиль
    gender = Column(String(10))  # male, female
    age = Column(Integer)
    height_cm = Column(Integer)
    weight_kg = Column(Float)
    goal = Column(String(50))  # lose_weight, gain_muscle, stay_fit
    level = Column(String(50))  # beginner, intermediate
    workout_type = Column(String(50))  # home, gym
    
    # Напоминания
    reminder_enabled = Column(Boolean, default=False)
    reminder_time = Column(String(5))  # HH:MM format
    reminder_days = Column(JSON)  # список дней недели: ["monday", "tuesday", ...]
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user_workouts = relationship("UserWorkout", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, goal={self.goal})>"


class Workout(Base):
    """Шаблон тренировки"""
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False)  # уникальный код
    title = Column(String(200), nullable=False)
    
    # Фильтры
    level = Column(String(50), nullable=False)  # beginner, intermediate
    workout_type = Column(String(50), nullable=False)  # home, gym
    goal = Column(String(50), nullable=False)  # lose_weight, gain_muscle, stay_fit
    day_index = Column(Integer, nullable=False)  # 0-6 (понедельник-воскресенье)
    
    # Упражнения (JSON)
    # Формат: [{"name": "Отжимания", "sets": 3, "reps": "10-15"}, ...]
    exercises_json = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user_workouts = relationship("UserWorkout", back_populates="workout")
    
    def __repr__(self):
        return f"<Workout(code={self.code}, title={self.title})>"


class UserWorkout(Base):
    """Выполненная тренировка пользователя"""
    __tablename__ = "user_workouts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    
    date = Column(Date, nullable=False, default=datetime.utcnow)
    completed = Column(Boolean, default=True)
    feeling = Column(String(20))  # easy, normal, hard
    comment = Column(String(500))  # опционально
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="user_workouts")
    workout = relationship("Workout", back_populates="user_workouts")
    
    def __repr__(self):
        return f"<UserWorkout(user_id={self.user_id}, workout_id={self.workout_id}, date={self.date})>"
