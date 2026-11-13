from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI

from api import media_router
from broker import connect_rabbit, declare_likes_queue
from core import setup_logger
from database import REDIS_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    redis_client: aioredis.Redis = aioredis.from_url(
        REDIS_URL, decode_responses=True, max_connections=50
    )

    rabbit = await connect_rabbit()
    channel = await rabbit.channel()
    await declare_likes_queue(channel)

    app.state.redis = redis_client
    app.state.rabbit = rabbit
    app.state.rabbit_channel = channel

    yield

    await app.state.rabbit.close()
    await app.state.redis.close()


app = FastAPI(title="High Load API", lifespan=lifespan)
app.include_router(media_router)


@app.get("/health")
def read_root():
    return {"status": "ok"}
