from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import media_router
from core import setup_logger


@asynccontextmanager
async def lifespan(app):
    setup_logger()
    yield
    await app.state.session.close()


app = FastAPI(title="High Load API")
app.include_router(media_router)


@app.get("/health")
def read_root():
    return {"status": "ok"}
