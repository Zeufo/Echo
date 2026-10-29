import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query
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


# TODO: CHECK BELLOW

# ============================================================
# schemas.py
# ============================================================

# TODO: PostCreate (тело POST /posts/)
#   - author_id: uuid.UUID
#   - text: str, ограничение длины как в колонке (max_length=1024), min_length=1

# TODO: LikeCreate (тело POST /posts/{post_id}/like)
#   - user_id: uuid.UUID

# TODO (по желанию): PostOut: id, text, likes_count
#   response_model ставим только на POST /posts/ (холодная ручка).
#   На GET /posts/{id} пока тоже можно, но позже это будет эксперимент
#   с замером "с response_model / без".


# ============================================================
# services/posts.py  (вся работа с БД здесь, хендлеры тонкие)
# При переходе на Redis/RabbitMQ меняем в основном эти функции.
# ============================================================

# TODO: create_post(session, author_id, text) -> Post
#   1. создать Post(id=uuid4(), author_id=..., text=..., likes_count=0)
#   2. session.add + commit
#   3. вернуть созданный пост

# TODO: get_post(session, post_id) -> Post | None
#   1. select Post where id == post_id
#   2. вернуть пост или None (404 решает хендлер)

# TODO: add_like(session, post_id, user_id) -> результат: ok / not_found / duplicate
#   Всё в ОДНОЙ транзакции:
#   1. INSERT в post_likes (post_id, user_id)
#   2. UPDATE posts SET likes_count = likes_count + 1 WHERE id = post_id
#      ВАЖНО: инкремент на стороне SQL (likes_count + 1), а не "прочитал в Python,
#      прибавил, записал" - иначе потерянные обновления.
#   3. commit
#   Ошибки:
#   - IntegrityError на PK (post_id, user_id) -> rollback, вернуть duplicate (409)
#   - IntegrityError на FK (поста нет) -> rollback, вернуть not_found (404)
#     (различить по имени констрейнта или проверкой rowcount у UPDATE)

# TODO: get_top_posts(session, limit=20) -> list[Post]
#   SELECT ... ORDER BY likes_count DESC LIMIT 20
#   Индекс на likes_count НЕ добавляем (честный наивный baseline),
#   зафиксировать это в README.
#   Решение "топ по общему числу лайков, а не за день" тоже записать в README.


# ============================================================
# routers/posts.py
# ============================================================

# router = APIRouter(prefix="/api/v1")

# POST /posts/  -> status_code=201
#   - тело: PostCreate
#   - вызвать create_post
#   - вернуть {"id": post.id}

# GET /posts/{post_id}  -> 200
#   - post_id: uuid.UUID (Path, FastAPI сам вернёт 422 на кривой UUID)
#   - вызвать get_post
#   - если None -> HTTPException(404)
#   - вернуть id, text, likes_count

# POST /posts/{post_id}/like  -> status_code=202
#   - тело: LikeCreate
#   - вызвать add_like
#   - not_found -> 404, duplicate -> 409, ok -> вернуть пустой ответ / {"status": "accepted"}
#   - НЕ 500 ни при каких обстоятельствах (иначе в замере будут ложные ошибки)
#   - ПОМНИТЬ: в v3 эта ручка перестанет ходить в БД (Redis INCR + RabbitMQ),
#     контракт (202) при этом остаётся тем же

# GET /feed/top  -> 200
#   - вызвать get_top_posts(limit=20)
#   - вернуть список из id, text, likes_count


# ============================================================
# Перед замером (проверить руками через Swagger)
# ============================================================
# [ ] создание поста -> 201 и id
# [ ] чтение существующего -> 200, несуществующего -> 404
# [ ] лайк -> 202, второй лайк того же юзера -> 409, лайк на левый post_id -> 404
# [ ] кривой UUID в пути -> 422
# [ ] likes_count в БД совпадает с числом строк в post_likes

# ============================================================
# Дальше (после замера v1-baseline, поставить git-тег v1-baseline)
# ============================================================
# 1. locustfile: чтения одного поста / лайки одного поста (каждый раз новый user_id) / микс 90/10
# 2. скрипт одного прогона: чистка БД и Redis -> сидирование -> locust headless -> CSV
# 3. v2: кэш на чтение в Redis (GET /posts/{id}), замер, тег v2-redis-read
# 4. v3: INCR в Redis + публикация в RabbitMQ + воркер с батчингом, замер, тег v3-rabbit


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_local_session() as session:
        yield session


@router.post(
    "/posts/",
    summary="make your post",
)
async def make_post(
    text: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> None:
    post_id = uuid.uuid4()
    return await create_post_service(session, post_id, text)


@router.get(
    "/posts/{post_id}",
    summary="Get a post by id",
)
async def get_post(
    post_id: uuid.UUID = Path(),
    session: AsyncSession = Depends(get_session),
) -> None:
    try:
        return await get_post_service(session, post_id)
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
) -> None:
    try:
        return await add_like_service(session, post_id, user_id)
    except AlreadyLikedError:
        raise HTTPException(status_code=409, detail="You already liked this post")


@router.get(
    "/feed/top",
    summary="get 10 popular posts",
)
async def get_top_post(session: AsyncSession = Depends(get_session)) -> None:
    return await get_top_posts_service(session)
