from fastapi import APIRouter

from src.twitch.routers.v1.categories_router import router as categories_router
from src.twitch.routers.v1.streams_router import router as streams_router
from src.twitch.routers.v1.users_router import router as users_router

router = APIRouter(prefix="")

router.include_router(categories_router, prefix="/categories")
router.include_router(streams_router, prefix="/streams")
router.include_router(users_router, prefix="/users")
