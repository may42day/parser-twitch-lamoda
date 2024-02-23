from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.resources.kafka import producer_send_one
from src.twitch.repository.users_repository import (
    clear_users_data,
    get_user_data,
    get_users_data,
)
from src.twitch.services.users_services import auto_parse_all_users, parse_specific_user


router = APIRouter()


@router.get("/auto-parse")
@cache(expire=1200)
async def parse_user():
    """
    API to start auto-parsing users of all streams in database.
    """

    await clear_users_data()
    await producer_send_one(auto_parse_all_users)
    return {"message": "Parsing started"}


@router.get("/parse")
@cache(expire=600)
async def parse_user(
    user_id: str = None,
    login: str = None,
):
    """
    API to start parsing users.

    Args:
    - user_id (str, optional) - user_id for searching user.
    - login (str, optional) - login for searching user.
    """
    if not user_id and not login:
        return {"error": "user_id or login must be specified"}

    await producer_send_one(parse_specific_user, user_id, login)
    return {"message": "Parsing started"}


@router.get("/")
@cache(expire=60)
async def get_users():
    """
    API to get all users data.
    """
    data = await get_users_data()

    for item in data:
        item["_id"] = str(item["_id"])

    return data


@router.get("/clear")
async def clear_users():
    """
    API to clear users collection.
    """
    count = await clear_users_data()
    return {"message": f"Users cleared ({count})"}


@router.get("/{identifier}")
@cache(expire=60)
async def get_specific_user(identifier: str):
    """
    API to get specific user data.

    Args:
    - identifier (str) - user's id or login to get user.
    """
    data = await get_user_data(identifier=identifier)
    if data:
        del data["_id"]
    return data
