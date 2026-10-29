import asyncio
import json
import os
import random
import uuid

from dotenv import load_dotenv
from sqlalchemy import CheckConstraint, String, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Загрузка переменных окружения
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "my_database")

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_local_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Posts(Base):
    __tablename__ = "posts"
    __table_args__ = (CheckConstraint("likes_count >= 0"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(1024))
    likes_count: Mapped[int] = mapped_column(nullable=False, default=0)


async def seed_database():
    # Генерируем 10 000 UUID
    random.seed(42)
    namespace = uuid.NAMESPACE_DNS
    uuids = [uuid.uuid5(namespace, f"post_index_{i}") for i in range(10000)]

    async with async_local_session() as session:
        # 1. Удаляем только строки/записи из таблицы posts (саму таблицу НЕ трогаем)
        await session.execute(delete(Posts))
        await session.commit()

        # 2. Формируем новые записи
        posts_to_insert = [
            Posts(id=uid, text=f"Initial seed post #{i}", likes_count=0)
            for i, uid in enumerate(uuids)
        ]

        # 3. Вставляем пачками по 1000 штук
        batch_size = 1000
        for i in range(0, len(posts_to_insert), batch_size):
            session.add_all(posts_to_insert[i : i + batch_size])
            await session.commit()

    # Сохраняем новые UUID в JSON-файл (файл перезаписывается начисто)
    with open("posts_uuids.json", "w") as f:
        json.dump([str(u) for u in uuids], f)

    print(f"Старые записи удалены. Успешно добавлено {len(uuids)} новых постов.")


if __name__ == "__main__":
    asyncio.run(seed_database())
