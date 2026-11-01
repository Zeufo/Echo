import uuid
from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_local_session
from services import (
    AlreadyLikedError,
    PostNotFoundError,
    add_like_service,
    create_post_service,
    get_post_service,
    get_top_posts_service,
)

router = APIRouter(prefix="/api/v1")


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_local_session() as session:
        yield session


async def get_redis_session(request: Request) -> aioredis.Redis:
    return request.app.state.redis


@router.post(
    "/posts/",
    summary="make your post",
)
async def make_post(
    text: str = "",
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis_session),
) -> None:
    post_id = uuid.uuid4()
    return await create_post_service(redis, session, post_id, text)


@router.get(
    "/posts/{post_id}",
    summary="Get a post by id",
)
async def get_post(
    post_id: uuid.UUID = Path(),
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis_session),
) -> None:
    try:
        return await get_post_service(redis, session, post_id)
    except PostNotFoundError:
        raise HTTPException(status_code=404, detail="Post not found")


@router.post(
    "/posts/{post_id}/like",
    summary="add your like to a post",
)
async def give_like(
    user_id: int,
    post_id: uuid.UUID = Path(),
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis_session),
) -> None:
    try:
        return await add_like_service(redis, session, post_id, user_id)
    except AlreadyLikedError:
        raise HTTPException(status_code=409, detail="You already liked this post")


@router.get(
    "/feed/top",
    summary="get 10 popular posts",
)
async def get_top_post(
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis_session),
) -> None:
    return await get_top_posts_service(redis, session)
