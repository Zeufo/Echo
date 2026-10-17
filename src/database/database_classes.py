import abc
import typing
from datetime import date, time

from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import DATABASE_URL


@typing.final
class DataBaseCRUD:
    @staticmethod
    async def create_post(session: AsyncSession) -> None: ...

    @staticmethod
    async def get_post() -> None: ...

    @staticmethod
    async def add_like() -> None: ...

    @staticmethod
    async def get_top() -> None: ...
