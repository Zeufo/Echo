import abc
import typing
import uuid
from datetime import date, time

from loguru import logger
from sqlalchemy import and_, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Likes, Posts


@typing.final
class DataBaseCRUD:
    @staticmethod
    async def create_post(
        session: AsyncSession, post_id: uuid.UUID, text: str | None = None
    ) -> None:
        session.add(Posts(id=post_id, text=text))
        await session.commit()

    @staticmethod
    async def get_post(session: AsyncSession, post_id: uuid.UUID) -> None | Posts:
        return await session.get(Posts, post_id)

    @staticmethod
    async def add_like(session: AsyncSession, post_id: uuid.UUID, user_id: int) -> None:
        session.add(Likes(post_id=post_id, user_id=user_id))
        stmt = (
            update(Posts)
            .where(Posts.id == post_id)
            .values(likes_count=Posts.likes_count + 1)
        )
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def get_top(session: AsyncSession, limit: int = 20) -> typing.Sequence[Posts]:
        stmt = select(Posts).order_by(Posts.likes_count.desc()).limit(limit)

        result = await session.execute(stmt)

        return result.scalars().all()

    @staticmethod
    async def can_like(session: AsyncSession, post_id: uuid.UUID, user_id: int) -> bool:
        stmt = select(Likes).where(Likes.post_id == post_id, Likes.user_id == user_id)
        result = await session.execute(stmt)
        logger.debug(f"result is {result}")

        return result.scalar() is None

    @staticmethod
    async def get_all_post_ids(session: AsyncSession, limit: int = 5000) -> list[uuid.UUID]:
        stmt = select(Posts.id).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())
