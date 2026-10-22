import os
import uuid
from datetime import date, datetime, time
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import (
    UUID,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Time,
    create_engine,
    func,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

CURRENT_FILE_PATH = Path(__file__).resolve()
SRC_DIR = next(p for p in CURRENT_FILE_PATH.parents if p.name == "src")
DOTENV_PATH = SRC_DIR.parent / ".env"


load_dotenv(dotenv_path=DOTENV_PATH)

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "my_database")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL, echo=True)
async_local_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase): ...


class Posts(Base):
    __tablename__ = "posts"
    __table_args__ = (CheckConstraint("likes_count >= 0"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(1024))
    likes_count: Mapped[int] = mapped_column(nullable=False, default=0)


class Likes(Base):
    __tablename__ = "post_likes"
    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(primary_key=True)
