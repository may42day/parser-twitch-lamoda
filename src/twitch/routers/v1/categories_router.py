from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.twitch.repository.categories_repository import (
    clear_categories_data,
    get_categories_data,
    get_category_data,
)
from src.twitch.services.categories_services import (
    auto_parse_all_categories,
    parse_category,
    parse_top_categories,
)
from src.resources.kafka import producer_send_one

router = APIRouter()


@router.get("/auto-parse")
@cache(expire=1200)
async def auto_parse_categories():
    """
    API to start auto-parsing categories/games.

    Parses every category/game by 100 items per page.
    """

    await clear_categories_data()
    await producer_send_one(auto_parse_all_categories)
    return {"message": "Parsing started"}


@router.get("/top/parse")
@cache(expire=600)
async def parse_categories(
    after: str = None,
    before: str = None,
    first: int = None,
):
    """
    API to start parsing categories/games.

    Args:
    - after (str, optional) - pagination param used to get the next page of results.
    - before (str, optional) - pagination param used to get the previous page of results.
    - first (int, optional, max 100) - the maximum number of items to return per page in the response.
    """

    await producer_send_one(parse_top_categories, first, after, before)
    return {"message": "Parsing started"}


@router.get("/parse")
@cache(expire=600)
async def parse_specific_category(
    id: str = None,
    name: str = None,
    igdb_id: str = None,
):
    """
    API to start parsing specific category or game by its id.

    Args:
    - id (str) - category/game id.
    - name (str) - category/game name for searching.
    - igdb_id (str) - category/game igdb id.
    """
    if not id and not name and not igdb_id:
        return {"error": "id or name or igdb_id must be specified"}

    await producer_send_one(parse_category, id, name, igdb_id)

    return {"message": "Parsing started"}


@router.get("/")
@cache(expire=60)
async def get_categories():
    """
    API to get all categories/games data.
    """
    data = await get_categories_data()

    for item in data:
        item["_id"] = str(item["_id"])

    return data


@router.get("/clear")
async def clear_categories():
    """
    API to clear categories/games collection.

    Returns message with amount of cleared categories.
    """
    count = await clear_categories_data()
    return {"message": f"Categories cleared ({count})"}


@router.get("/{category_id}")
@cache(expire=60)
async def get_specific_category(category_id: str):
    """
    API to get specific category/game data.

    Args:
    - id (str) - category/game id.
    """
    data = await get_category_data(category_id=category_id)
    if data:
        del data["_id"]
    return data
