from fastapi_cache.backends.redis import RedisBackend
from src.config import settings
from fastapi_cache import FastAPICache
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from src.resources.kafka import run_kafka
from src.twitch.client import TwitchAPIClient


twitch_client = TwitchAPIClient(
    client_id=settings.twitch_client_id, client_secret=settings.twitch_client_secret
)


async def get_twitch_client() -> TwitchAPIClient:
    """
    Twitch API client dependency for endpoints.
    """
    return twitch_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application initialization and termination logic.

    - inits project config,
    - creates connections with databases,
    - init caching,
    - run kafka consumer,
    """
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    asyncio.create_task(run_kafka())
    _check_config = settings
    yield


app = FastAPI(lifespan=lifespan)


from src.exceptions.handler import lamoda_exception_handler
from src.routers.api_v1_config import v1_api_router

app.include_router(v1_api_router)
