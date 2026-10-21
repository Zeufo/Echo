import typing
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database_classes import DataBaseCRUD


async def create_post_service(
    session: AsyncSession, post_id: uuid.UUID, text: str | None = None
) -> typing.Any:
    await DataBaseCRUD.create_post(session, post_id, text)
    return {"status": "ok", "id": str(post_id)}


async def get_post_service(session: AsyncSession, post_id: uuid.UUID) -> typing.Any:
    post = await DataBaseCRUD.get_post(session, post_id)
    if not post:
        return None
    return {"id": str(post.id), "text": post.text, "likes_count": post.likes_count}


async def add_like_service(
    session: AsyncSession, post_id: uuid.UUID, user_id: int
) -> typing.Any:
    try:
        await DataBaseCRUD.add_like(session, post_id, user_id)
        await session.commit()
        return {"status": "ok"}
    except Exception:
        await session.rollback()
        return {"status": "error"}


async def get_top_posts_service(session: AsyncSession, limit: int = 20) -> typing.Any:
    posts = await DataBaseCRUD.get_top(session, limit)
    if posts:
        return [
            {"id": str(p.id), "text": p.text, "likes_count": p.likes_count}
            for p in posts
        ]
