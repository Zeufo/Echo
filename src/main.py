from contextlib import asynccontextmanager

import redis
import redis.asyncio as aioredis
from fastapi import FastAPI

from api import media_router
from core import setup_logger
from database import REDIS_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    redis_client: aioredis.Redis = aioredis.from_url(
        REDIS_URL, decode_responses=True, max_connections=50
    )

    app.state.redis = redis_client
    yield
    await app.state.redis.close()


app = FastAPI(title="High Load API", lifespan=lifespan)
app.include_router(media_router)


@app.get("/health")
def read_root():
    return {"status": "ok"}
