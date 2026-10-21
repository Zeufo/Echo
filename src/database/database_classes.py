import abc
import typing
import uuid
from datetime import date, time

from loguru import logger
from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import DATABASE_URL
from src.database.models import Posts


@typing.final
class DataBaseCRUD:
    @staticmethod
    async def create_post(
        session: AsyncSession, post_id: uuid.UUID, text: str | None = None
    ) -> None:
        await session.add(Posts(id=post_id, text=text))
        await session.commit()

    @staticmethod
    async def get_post(session: AsyncSession, post_id: uuid.UUID) -> None:
        return await session.get(Posts, post_id)

    @staticmethod
    async def add_like(session: AsyncSession, post_id: uuid.UUID, user_id: int) -> None:
        stmt = (
            update(Posts)
            .where(Posts.id == post_id)
            .values(likes_count=Posts.likes_count + 1)
        )
        await session.execute(stmt)

    @staticmethod
    async def get_top(session: AsyncSession, limit: int = 20) -> typing.Sequence[Posts]:
        stmt = select(Posts).order_by(Posts.likes.desc()).limit(limit)
        result = await session.execute(stmt).all()
        return result.scalars().all()
