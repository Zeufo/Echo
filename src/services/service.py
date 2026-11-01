import json
import typing
import uuid

import redis
import redis.asyncio as aioredis
from fastapi import Request
from loguru import logger
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from database import DataBaseCRUD


class PostNotFoundError(Exception): ...


class AlreadyLikedError(Exception): ...


async def create_post_service(
    aioredis: aioredis.Redis,
    session: AsyncSession,
    post_id: uuid.UUID,
    text: str | None = None,
) -> typing.Any:
    await DataBaseCRUD.create_post(session, post_id, text)
    data = {"id": str(post_id), "text": text, "likes_count": 0}
    await aioredis.set(f"post:{post_id}", json.dumps(data), ex=60)
    return {"status": "ok", "id": str(post_id)}


async def get_post_service(
    aioredis: aioredis.Redis, session: AsyncSession, post_id: uuid.UUID
) -> typing.Any:
    post = await aioredis.get(f"post:{post_id}")
    if post:
        return json.loads(post)

    post = await DataBaseCRUD.get_post(session, post_id)
    if not post:
        raise PostNotFoundError()

    data = {"id": str(post.id), "text": post.text, "likes_count": post.likes_count}
    await aioredis.set(f"post:{post_id}", json.dumps(data), ex=60)
    return data


async def add_like_service(
    aioredis: aioredis.Redis,
    session: AsyncSession,
    post_id: uuid.UUID,
    user_id: int,
) -> typing.Any:
    try:
        can_like = await DataBaseCRUD.can_like(session, post_id, user_id)
        logger.debug(f"can_like: {can_like}")

        if not can_like:
            raise AlreadyLikedError()

        await DataBaseCRUD.add_like(session, post_id, user_id)
        await session.commit()
        await aioredis.delete(f"post:{post_id}")
        return {"status": "ok"}

    except AlreadyLikedError:
        raise
    except Exception:
        await session.rollback()


async def get_top_posts_service(
    aioredis: aioredis.Redis, session: AsyncSession, limit: int = 20
) -> typing.Any:
    posts = await aioredis.hget("top:1", "data")
    if posts:
        return json.loads(posts)

    posts = await DataBaseCRUD.get_top(session, limit)
    if posts:
        data = [
            {"id": str(p.id), "text": p.text, "likes_count": p.likes_count}
            for p in posts
        ]
        await aioredis.hset("top:1", mapping={"data": json.dumps(data)})
        await aioredis.expire("top:1", 20)
        return data
