from fastapi import APIRouter
from src.twitch.routers.v1_config import router as v1_twitch_router
from src.lamoda.router import router as v1_lamoda_router

v1_api_router = APIRouter(prefix="/api/v1")

v1_api_router.include_router(v1_twitch_router, prefix="/twitch", tags=["Twitch"])
v1_api_router.include_router(v1_lamoda_router, prefix="/lamoda", tags=["Lamoda"])
