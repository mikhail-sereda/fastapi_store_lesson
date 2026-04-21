from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Строка подключения для SQLite
DATABASE_LITE_URL = "sqlite:///ecommerce.db"

# Создаём Engine
engine = create_engine(DATABASE_LITE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)

# --------------- Асинхронное подключение к PostgreSQL -------------------------

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.setting import DATABASE_URL

# Создаём Engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
async_session_maker = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
